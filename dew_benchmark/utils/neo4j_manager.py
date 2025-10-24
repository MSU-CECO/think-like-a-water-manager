from neo4j import GraphDatabase
import sympy as sp


class Neo4jManager:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def build_knowledge_graph(self, equations, terms):
        """Build a complete knowledge graph with equations, variables, terms and their relationships"""
        with self.driver.session() as session:
            # Create constraints
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Equation) REQUIRE e.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (v:Variable) REQUIRE v.name IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Term) REQUIRE t.name IS UNIQUE")
            
            # Convert objects to dictionaries
            equations_dict = {eq.name: eq.to_dict() for eq in equations}
            terms_dict = [term.to_dict() for term in terms]
            
            # Create equation nodes
            for eq_name, eq_data in equations_dict.items():
                # Create equation node
                session.run("""
                    MERGE (e:Equation {id: $id})
                    SET e.name = $name, 
                        e.latex = $latex
                """, id=eq_data["id"], name=eq_name, latex=eq_data["latex"])
                
                # Create variable nodes and relationships
                for var_name, var_data in eq_data["variables"].items():
                    unit_str = str(var_data["unit"]) if var_data["unit"] else "dimensionless"
                    unit_latex = sp.latex(var_data["unit"]) if var_data["unit"] else ""
                    
                    session.run("""
                        MERGE (v:Variable {name: $var_name})
                        SET v.description = $description
                        WITH v
                        MATCH (e:Equation {id: $eq_id})
                        MERGE (e)-[:USES]->(v)
                        MERGE (u:Unit {name: $unit_name})
                        SET u.latex = $unit_latex
                        MERGE (v)-[:HAS_UNIT]->(u)
                    """, var_name=var_name, description=var_data["description"], 
                         eq_id=eq_data["id"], unit_name=unit_str, unit_latex=unit_latex)
            
            # Add equation dependencies
            for eq_name, eq_data in equations_dict.items():
                for dep_id in eq_data["dependencies"]:
                    session.run("""
                        MATCH (e1:Equation {id: $eq_id}), (e2:Equation {id: $dep_id})
                        MERGE (e1)-[:DEPENDS_ON]->(e2)
                    """, eq_id=eq_data["id"], dep_id=dep_id)
            
            # Add terms
            for term in terms_dict:
                session.run("""
                    MERGE (t:Term {name: $name})
                    SET t.display_name = $display_name,
                        t.symbol = $symbol,
                        t.definition = $definition,
                        t.common_unit = $common_unit
                """, **term)
            
            # Add term relationships
            for term in terms_dict:
                for related in term["related_terms"]:
                    session.run("""
                        MATCH (t1:Term {name: $term}), (t2:Term {name: $related})
                        MERGE (t1)-[:RELATED_TO]->(t2)
                    """, term=term["name"], related=related)
            
            # Connect variables to terms
            for term in terms_dict:
                if term["symbol"]:
                    session.run("""
                        MATCH (v:Variable {name: $var_name}), (t:Term {name: $term_name})
                        MERGE (v)-[:REPRESENTS]->(t)
                    """, var_name=term["symbol"], term_name=term["name"])
        
        print("Knowledge graph built successfully!")


    def get_hints(self, problem, include_terms=True):
        """Get hints for a problem from the Neo4j graph with automatic dependency resolution"""
        session = self.driver.session()
        
        hints = {
            "equations": {},
            "terms": {},
            "solution_path": []
        }
        
        # Get relevant equations
        for eq_id in problem["equations_used"]:
            equation_result = session.run("""
                MATCH (e:Equation {id: $eq_id})
                OPTIONAL MATCH (e)-[:USES]->(v:Variable)
                OPTIONAL MATCH (v)-[:HAS_UNIT]->(u:Unit)
                RETURN e.name as name, e.latex as latex, 
                       collect({name: v.name, description: v.description, 
                               unit: CASE WHEN u IS NOT NULL THEN u.name ELSE NULL END, 
                               unit_latex: CASE WHEN u IS NOT NULL THEN u.latex ELSE NULL END}) as variables
            """, eq_id=eq_id).single()
            
            if equation_result:
                hints["equations"][eq_id] = {
                    "name": equation_result["name"],
                    "latex": equation_result["latex"],
                    "variables": equation_result["variables"]
                }


        # Get relevant terms 
        term_names = problem["target_variables"] 
        
        # Option 1: First check if these terms exist in the database
        check_query = session.run("""
            MATCH (t:Term)
            RETURN t.name as name, t.symbol as symbol
        """)
        
        all_terms = {}
        for record in check_query:
            all_terms[record["name"]] = record["symbol"]
        
        # Match target variables to term symbols
        matched_terms = []
        for var in term_names:
            # Look for exact match first
            if var in all_terms:
                matched_terms.append(var)
            else:
                # Look for terms where the variable matches the symbol
                for term_name, symbol in all_terms.items():
                    if symbol == var:
                        matched_terms.append(term_name)
                        break
        
        if include_terms:
            # Now query for those terms
            term_results = session.run("""
                MATCH (t:Term)
                WHERE t.name IN $terms OR t.symbol IN $symbols
                OPTIONAL MATCH (t)-[:RELATED_TO]->(rt:Term)
                RETURN t.name as name, t.display_name as display_name, t.definition as definition,
                    collect({name: rt.name, display_name: rt.display_name, definition: rt.definition}) as related_terms
            """, terms=matched_terms, symbols=term_names)
            
            record_count = 0
            for record in term_results:
                record_count += 1
                hints["terms"][record["name"]] = {
                    "display_name": record["display_name"],
                    "definition": record["definition"],
                    "related_terms": record["related_terms"]
                }
        
            
        # Analyze equation dependencies for proper solution path
        eq_vars_map = {}
        for eq_id, eq_data in hints["equations"].items():
            eq_vars = [var["name"] for var in eq_data["variables"]]
            eq_vars_map[eq_id] = eq_vars
        
        
        # Map target variables to possible equations 
        target_equations = {}
        for target in problem["target_variables"]:
            target_equations[target] = []
            
            for eq_id, vars_list in eq_vars_map.items():
                if target in vars_list:
                    target_equations[target].append(eq_id)
        
        # Create a dependency graph for variables
        known_vars = set(problem["given_values"].keys())
        if "rho_s" not in known_vars and "rho_s" in problem.get("constants", {}):
            known_vars.add("rho_s")  # Add any constants
            
        # Determine which equations can be used to solve for specific variables
        solvable_equations = {}
        for eq_id, vars_list in eq_vars_map.items():
            for var in vars_list:
                # A variable is solvable from an equation if all other variables are known
                other_vars = set(vars_list) - {var}
                if other_vars.issubset(known_vars):
                    if var not in solvable_equations:
                        solvable_equations[var] = []
                    solvable_equations[var].append(eq_id)
        
        # Create a solution path by topological sorting of variable dependencies
        ordered_targets = []
        remaining_targets = set(problem["target_variables"])
        
        # Continue as long as we can solve for at least one more variable
        while remaining_targets and len(ordered_targets) < len(problem["target_variables"]):
            found = False
            
            for target in remaining_targets:
                # Check if we can solve this target with available equations and known variables
                usable_equations = []
                for eq_id in target_equations[target]:
                    other_vars = set(eq_vars_map[eq_id]) - {target}
                    if other_vars.issubset(known_vars):
                        usable_equations.append(eq_id)
                
                if usable_equations:
                    ordered_targets.append(target)
                    remaining_targets.remove(target)
                    known_vars.add(target)  # This variable is now known for later equations
                    
                    # Store only the usable equations for this target
                    target_equations[target] = usable_equations
                    found = True
                    break
            
            if not found:
                # If we couldn't find a new solvable variable, add remaining targets in any order
                ordered_targets.extend(list(remaining_targets))
                break
        
        # Create solution path from ordered targets
        for target in ordered_targets:
            # Only include equations that can actually be used to solve for this variable
            # with the known variables at this stage
            eq_choices = target_equations[target]
            if eq_choices:
                hints["solution_path"].append({
                    "target": target,
                    "equations": eq_choices
                })
        
        session.close()
        return hints


    def get_variables_with_units(self, variable_names=None):
        """
        Returns a dictionary mapping variable names to their corresponding units.
        
        Args:
            variable_names (list, optional): List of variable names to filter for.
                                             If None, returns all variables.
        
        Returns:
            dict: Dictionary with variable names as keys and unit strings as values
        """
        with self.driver.session() as session:
            if variable_names:
                results = session.run("""
                    MATCH (v:Variable)-[:HAS_UNIT]->(u:Unit)
                    WHERE v.name IN $var_names
                    RETURN v.name as variable_name, u.name as unit_name
                """, var_names=variable_names)
            else:
                results = session.run("""
                    MATCH (v:Variable)-[:HAS_UNIT]->(u:Unit)
                    RETURN v.name as variable_name, u.name as unit_name
                """)
            
            variables_units_map = {}
            for record in results:
                variable_name = record["variable_name"]
                unit_name = record["unit_name"]
                variables_units_map[variable_name] = unit_name
                
            return variables_units_map

