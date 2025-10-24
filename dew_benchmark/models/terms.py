class Term:
    def __init__(self, name, display_name, symbol, definition, common_unit, related_terms=None):
        self.name = name
        self.display_name = display_name
        self.symbol = symbol
        self.definition = definition
        self.common_unit = common_unit
        self.related_terms = related_terms or []
    
    def to_dict(self):
        """Convert to dictionary for Neo4j and JSON serialization"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "symbol": self.symbol,
            "definition": self.definition,
            "common_unit": self.common_unit,
            "related_terms": self.related_terms
        }