"""
DSL Parser (Domain Specific Language)
-------------------------------------
Handles the parsing and interpretation of the validation rule language.
Uses PLY (Python Lex-Yacc) to evaluate readable string rules against data.

Supported Features:
- Arithmetic: '4C = 1C + 2C'
- Datatypes: '1C IS ALPHANUM'
- Comparisons: '3C > 100', '2C = "USD"'
- Patterns: '1C STARTS_WITH "TXN"'
- Ranges: '4C BETWEEN 10 AND 1000'
- Existence: '1C REQUIRED'

Author: Sriram
Last Updated: Jan 2026
"""

import ply.lex as lex
import ply.yacc as yacc
import re

# =============================================
# LEXER - Token Definitions
# =============================================

# List of token names used by the parser
tokens = [
    "COLUMN_REF",  # Matches '1C', '2C'
    "NUMBER",      # Matches integers and floats
    "STRING",      # Matches quoted strings "value"
    "PLUS", "MINUS", "MULTIPLY", "DIVIDE",
    "EQUALS", "NOT_EQUALS",
    "GREATER", "LESS", "GREATER_EQUAL", "LESS_EQUAL",
    "LPAREN", "RPAREN",
]

# Keywords reserved in the DSL
keywords = {
    "IS": "IS",
    "BETWEEN": "BETWEEN",
    "MATCHES": "MATCHES",
    "CONTAINS": "CONTAINS",
    "NOT_CONTAINS": "NOT_CONTAINS",
    "STARTS_WITH": "STARTS_WITH",
    "ENDS_WITH": "ENDS_WITH",
    "ALPHANUM": "ALPHANUM",
    "NUMERIC": "NUMERIC",
    "INTEGER": "INTEGER",
    "FLOAT": "FLOAT",
    "STRING_TYPE": "STRING_TYPE",
    "REQUIRED": "REQUIRED",
    "AND": "AND",
}

tokens.extend(list(keywords.values()))

# --- Regex/String matching for Tokens ---
t_PLUS = r"\+"
t_MINUS = r"-"
t_MULTIPLY = r"\*"
t_DIVIDE = r"/"
t_EQUALS = r"="
t_NOT_EQUALS = r"!="
t_GREATER = r">"
t_LESS = r"<"
t_GREATER_EQUAL = r">="
t_LESS_EQUAL = r"<="
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_ignore = " \t" # Ignore spaces and tabs

# --- Keyword Token Functions (Case Insensitive) ---
def t_IS(t):
    r"[Ii][Ss]"
    return t

def t_BETWEEN(t):
    r"[Bb][Ee][Tt][Ww][Ee][Ee][Nn]"
    return t

def t_AND(t):
    r"[Aa][Nn][Dd]"
    return t

def t_MATCHES(t):
    r"[Mm][Aa][Tt][Cc][Hh][Ee][Ss]"
    return t

def t_CONTAINS(t):
    r"[Cc][Oo][Nn][Tt][Aa][Ii][Nn][Ss]"
    return t

def t_NOT_CONTAINS(t):
    r"[Nn][Oo][Tt]_[Cc][Oo][Nn][Tt][Aa][Ii][Nn][Ss]"
    return t

def t_STARTS_WITH(t):
    r"[Ss][Tt][Aa][Rr][Tt][Ss]_[Ww][Ii][Tt][Hh]"
    return t

def t_ENDS_WITH(t):
    r"[Ee][Nn][Dd][Ss]_[Ww][Ii][Tt][Hh]"
    return t

def t_ALPHANUM(t):
    r"[Aa][Ll][Pp][Hh][Aa][Nn][Uu][Mm]"
    return t

def t_NUMERIC(t):
    r"[Nn][Uu][Mm][Ee][Rr][Ii][Cc]"
    return t

def t_INTEGER(t):
    r"[Ii][Nn][Tt][Ee][Gg][Ee][Rr]"
    return t

def t_FLOAT(t):
    r"[Ff][Ll][Oo][Aa][Tt]"
    return t

def t_STRING_TYPE(t):
    r"[Ss][Tt][Rr][Ii][Nn][Gg](_[Tt][Yy][Pp][Ee])?"
    return t

def t_REQUIRED(t):
    r"[Rr][Ee][Qq][Uu][Ii][Rr][Ee][Dd]"
    return t

def t_COLUMN_REF(t):
    r"\d+[Cc]"
    t.value = int(t.value[:-1])  # Convert '1C' -> 1
    return t

def t_STRING(t):
    r"\"[^\"]*\" "
    t.value = t.value[1:-1]  # Strip quotes
    return t

def t_NUMBER(t):
    r"\d+(\.\d+)?"
    if "." in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

def t_error(t):
    # Skip illegal characters
    # print(f"Illegal character '{t.value[0]}'") 
    t.lexer.skip(1)


# =============================================
# PARSER - Grammar Rules
# =============================================

# Precedence for math operations
precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "MULTIPLY", "DIVIDE"),
)

# Global storage for parsed rules
rules_list = []

def p_rule_statement(p):
    """rule_statement : arithmetic_rule
    | datatype_rule
    | comparison_rule
    | pattern_rule
    | range_rule
    | validation_rule"""
    p[0] = p[1]
    rules_list.append(p[1])


# 1. Arithmetic rule: 4C = 1C + 2C
def p_arithmetic_rule(p):
    """arithmetic_rule : COLUMN_REF EQUALS expression"""
    p[0] = {"type": "arithmetic", "target": p[1], "expression": p[3]}

# 2. Datatype rule: 1C IS ALPHANUM
def p_datatype_rule(p):
    """datatype_rule : COLUMN_REF IS datatype"""
    p[0] = {"type": "datatype", "column": p[1], "datatype": p[3].lower()}

def p_datatype(p):
    """datatype : ALPHANUM
    | NUMERIC
    | INTEGER
    | FLOAT
    | STRING_TYPE"""
    p[0] = p[1]

# 3. Comparison rule: 2C > 100
def p_comparison_rule(p):
    """comparison_rule : COLUMN_REF comparison_operator value"""
    p[0] = {"type": "comparison", "column": p[1], "operator": p[2], "value": p[3]}

def p_comparison_operator(p):
    """comparison_operator : EQUALS
    | NOT_EQUALS
    | GREATER
    | LESS
    | GREATER_EQUAL
    | LESS_EQUAL"""
    p[0] = p[1]

# 4. Pattern rule: 3C STARTS_WITH "TXN"
def p_pattern_rule(p):
    """pattern_rule : COLUMN_REF pattern_operator STRING"""
    p[0] = {
        "type": "pattern",
        "column": p[1],
        "operator": p[2].lower(),
        "pattern": p[3],
    }

def p_pattern_operator(p):
    """pattern_operator : MATCHES
    | CONTAINS
    | NOT_CONTAINS
    | STARTS_WITH
    | ENDS_WITH"""
    p[0] = p[1]

# 5. Range rule: 4C BETWEEN 10 AND 20
def p_range_rule(p):
    """range_rule : COLUMN_REF BETWEEN NUMBER AND NUMBER"""
    p[0] = {"type": "range", "column": p[1], "min": p[3], "max": p[5]}

# 6. Validation rule: 1C REQUIRED
def p_validation_rule(p):
    """validation_rule : COLUMN_REF REQUIRED"""
    p[0] = {"type": "validation", "column": p[1], "validation": "required"}

# Helpers
def p_value(p):
    """value : NUMBER
    | STRING
    | COLUMN_REF"""
    p[0] = p[1]

def p_expression(p):
    """expression : term
    | expression PLUS term
    | expression MINUS term"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ("binary", p[2], p[1], p[3])

def p_term(p):
    """term : factor
    | term MULTIPLY factor
    | term DIVIDE factor"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ("binary", p[2], p[1], p[3])

def p_factor(p):
    """factor : COLUMN_REF
    | NUMBER
    | LPAREN expression RPAREN"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error")


# =============================================
# RULE INTERPRETER CLASS
# =============================================

class DSLInterpreter:
    """
    Main interpreter class.
    1. Parses rule strings into AST (Abstract Syntax Tree).
    2. Validates data dictionaries against proper rules.
    """

    def __init__(self):
        global rules_list
        rules_list = []
        self.lexer = lex.lex()
        self.parser = yacc.yacc(debug=False)
        self.rules = []

    def parse_rule(self, rule_text):
        """Parse a single line of rule text."""
        global rules_list
        rules_list = []

        try:
            result = self.parser.parse(rule_text, lexer=self.lexer)
            if rules_list:
                rule = rules_list[0]
                self.rules.append(rule)
                return rule
            return result
        except Exception as e:
            print(f"Error parsing rule: {e}")
            return None

    def parse_multiple_rules(self, rules_text):
        """Parse a block of rules separated by newlines."""
        parsed_rules = []

        for line in rules_text.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                parsed = self.parse_rule(line)
                if parsed:
                    parsed_rules.append(parsed)

        return parsed_rules

    def evaluate_expression(self, expr, data):
        """Recursive evaluation of arithmetic expressions."""
        if isinstance(expr, (int, float)):
            # If int, it *could* be a column index from the parser
            if isinstance(expr, int) and expr in data:
                return data.get(expr)
            return expr
        elif isinstance(expr, tuple):
            if expr[0] == "binary":
                op = expr[1]
                left = self.evaluate_expression(expr[2], data)
                right = self.evaluate_expression(expr[3], data)

                try:
                    left_num = float(left)
                    right_num = float(right)

                    if op == "+": return left_num + right_num
                    elif op == "-": return left_num - right_num
                    elif op == "*": return left_num * right_num
                    elif op == "/": return left_num / right_num if right_num != 0 else 0
                except (ValueError, TypeError):
                    return None
        return None

    def validate_rule(self, rule, data):
        """
        Executes a single parsed rule against a data row.
        Returns: {passed: bool, message: str}
        """
        rule_type = rule.get("type")

        # --- A. Arithmetic Validation ---
        if rule_type == "arithmetic":
            target = rule["target"] # Target Column
            expr = rule["expression"] # Expected Calculation

            expected = self.evaluate_expression(expr, data)
            actual = data.get(target)

            if actual is None or expected is None:
                return {"passed": False, "message": f"Missing data for calc on col {target}"}

            try:
                actual_num = float(actual)
                expected_num = float(expected)
                passed = abs(actual_num - expected_num) < 0.001
            except (ValueError, TypeError):
                return {"passed": False, "message": f"Non-numeric values in calc col {target}"}

            return {"passed": passed, "message": f"Col {target}C = {actual}, Expected: {expected:.2f}"}

        # --- B. Datatype Validation ---
        elif rule_type == "datatype":
            column = rule["column"]
            expected_type = rule["datatype"]
            value = data.get(column)

            if value is None:
                return {"passed": False, "message": f"Column {column}C is empty"}

            str_value = str(value)

            if expected_type == "alphanum":
                passed = str_value.isalnum()
            elif expected_type == "numeric":
                passed = str_value.replace(".", "", 1).replace("-", "", 1).isdigit()
            elif expected_type == "integer":
                passed = str_value.lstrip("-").isdigit()
            elif expected_type == "float":
                try:
                    float(value)
                    passed = True
                except:
                    passed = False
            elif expected_type == "string_type":
                passed = isinstance(value, str) or isinstance(value, int) # Flexible check
            else:
                passed = False

            return {"passed": passed, "message": f"Col {column}C is {expected_type}: {passed}"}

        # --- C. Comparison Validation ---
        elif rule_type == "comparison":
            column = rule["column"]
            operator = rule["operator"]
            expected_value = rule["value"]
            actual_value = data.get(column)

            # Resolve expected value if it's a column reference
            if isinstance(expected_value, int) and expected_value in data:
                 expected_value = data.get(expected_value)

            if actual_value is None:
                return {"passed": False, "message": f"Column {column}C is empty"}

            # Numeric comparison logic
            try:
                actual_num = float(actual_value)
                expected_num = float(expected_value)

                if operator == "=": passed = abs(actual_num - expected_num) < 0.001
                elif operator == "!=": passed = abs(actual_num - expected_num) > 0.001
                elif operator == ">": passed = actual_num > expected_num
                elif operator == "<": passed = actual_num < expected_num
                elif operator == ">=": passed = actual_num >= expected_num
                elif operator == "<=": passed = actual_num <= expected_num
                else: passed = False
            except (ValueError, TypeError):
                # Fallback to string comparison
                actual_str = str(actual_value)
                expected_str = str(expected_value)

                if operator == "=": passed = actual_str == expected_str
                elif operator == "!=": passed = actual_str != expected_str
                else: passed = False

            return {"passed": passed, "message": f"Col {column}C ({actual_value}) {operator} {expected_value}"}

        # --- D. Pattern Matching ---
        elif rule_type == "pattern":
            column = rule["column"]
            operator = rule["operator"]
            pattern = rule["pattern"]
            value = str(data.get(column, ""))

            if operator == "matches":
                passed = bool(re.match(pattern, value))
            elif operator == "contains":
                passed = pattern in value
            elif operator == "not_contains":
                passed = pattern not in value
            elif operator == "starts_with":
                passed = value.startswith(pattern)
            elif operator == "ends_with":
                passed = value.endswith(pattern)
            else:
                passed = False

            return {"passed": passed, "message": f"Col {column}C {operator} '{pattern}'"}

        # --- E. Range Check ---
        elif rule_type == "range":
            column = rule["column"]
            min_val = rule["min"]
            max_val = rule["max"]
            value = data.get(column)

            try:
                v = float(value)
                passed = min_val <= v <= max_val
            except:
                passed = False
            
            return {"passed": passed, "message": f"Col {column}C ({value}) between {min_val}-{max_val}"}

        # --- F. Required Field ---
        elif rule_type == "validation": # Type validation currently used for REQUIRED
            column = rule["column"]
            validation = rule["validation"]
            value = data.get(column)

            if validation == "required":
                passed = value is not None and str(value).strip() != ""
            else:
                passed = False

            return {"passed": passed, "message": f"Col {column}C Required"}

        return {"passed": False, "message": f"Unknown rule type: {rule_type}"}

    def validate_data(self, data):
        """Validate a full row against all loaded rules."""
        results = []
        for rule in self.rules:
            result = self.validate_rule(rule, data)
            results.append({
                "rule": rule,
                "passed": result["passed"],
                "message": result["message"]
            })
        return results
