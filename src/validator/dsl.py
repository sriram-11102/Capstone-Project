"""
DSL Parser for Real-Time File Monitoring System
Simplified version with clean grammar
"""

import ply.lex as lex
import ply.yacc as yacc
import re

# =============================================
# LEXER - Token Definitions
# =============================================

# List of token names
tokens = [
    "COLUMN_REF",  # e.g., 1C, 2C, 51C
    "NUMBER",  # Integer or float
    "STRING",  # Quoted string
    "PLUS",
    "MINUS",
    "MULTIPLY",
    "DIVIDE",
    "EQUALS",
    "NOT_EQUALS",
    "GREATER",
    "LESS",
    "GREATER_EQUAL",
    "LESS_EQUAL",
    "LPAREN",
    "RPAREN",
]

# Add keyword tokens
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

# Add keywords to tokens
tokens.extend(list(keywords.values()))

# Simple tokens
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
t_ignore = " \t"


# Define keyword tokens as functions for case-insensitive matching
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
    t.value = int(t.value[:-1])  # Remove 'C' or 'c'
    return t


def t_STRING(t):
    r"\"[^\"]*\" "
    t.value = t.value[1:-1]  # Remove quotes
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
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


# =============================================
# PARSER - Grammar Rules (Simplified)
# =============================================

# Precedence rules
precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "MULTIPLY", "DIVIDE"),
)

# Store parsed rules
rules_list = []


# Rule types
def p_rule_statement(p):
    """rule_statement : arithmetic_rule
    | datatype_rule
    | comparison_rule
    | pattern_rule
    | range_rule
    | validation_rule"""
    p[0] = p[1]
    rules_list.append(p[1])


# Arithmetic rule: 4C = 1C + 2C + 3C
def p_arithmetic_rule(p):
    """arithmetic_rule : COLUMN_REF EQUALS expression"""
    p[0] = {"type": "arithmetic", "target": p[1], "expression": p[3]}


# Datatype rule: 51C IS ALPHANUM
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


# Comparison rule: 10C > 0 or 30C = "ExpectedValue"
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


# Pattern rule: 40C CONTAINS "test"
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


# Range rule: 60C BETWEEN 10 AND 20
def p_range_rule(p):
    """range_rule : COLUMN_REF BETWEEN NUMBER AND NUMBER"""
    p[0] = {"type": "range", "column": p[1], "min": p[3], "max": p[5]}


# Validation rule: 70C REQUIRED
def p_validation_rule(p):
    """validation_rule : COLUMN_REF REQUIRED"""
    p[0] = {"type": "validation", "column": p[1], "validation": "required"}


# Value for comparison (can be number or string, but not column reference)
def p_value(p):
    """value : NUMBER
    | STRING"""
    p[0] = p[1]


# Expression for arithmetic (can be column references and numbers with operators)
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
# RULE INTERPRETER
# =============================================


class DSLInterpreter:
    """Interprets parsed DSL rules and applies them to data"""

    def __init__(self):
        global rules_list
        rules_list = []
        self.lexer = lex.lex()
        self.parser = yacc.yacc(debug=False)
        self.rules = []

    def parse_rule(self, rule_text):
        """Parse a single rule from text"""
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
        """Parse multiple rules separated by newlines"""
        parsed_rules = []

        for line in rules_text.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                parsed = self.parse_rule(line)
                if parsed:
                    parsed_rules.append(parsed)

        return parsed_rules

    def evaluate_expression(self, expr, data):
        """Evaluate an expression against data"""
        if isinstance(expr, (int, float)):
            # If it's an integer, it might be a column reference
            if isinstance(expr, int) and expr in data:
                return data.get(expr)
            return expr
        elif isinstance(expr, tuple):
            if expr[0] == "binary":
                op = expr[1]
                left = self.evaluate_expression(expr[2], data)
                right = self.evaluate_expression(expr[3], data)

                # Get actual values
                left_val = left
                right_val = right

                try:
                    left_num = float(left_val)
                    right_num = float(right_val)

                    if op == "+":
                        return left_num + right_num
                    elif op == "-":
                        return left_num - right_num
                    elif op == "*":
                        return left_num * right_num
                    elif op == "/":
                        return left_num / right_num if right_num != 0 else 0
                except (ValueError, TypeError):
                    return None
        return None

    def validate_rule(self, rule, data):
        """Validate a single rule against data"""
        rule_type = rule.get("type")

        if rule_type == "arithmetic":
            target = rule["target"]
            expr = rule["expression"]

            expected = self.evaluate_expression(expr, data)
            actual = data.get(target)

            if actual is None or expected is None:
                return {
                    "passed": False,
                    "message": f"Missing data for arithmetic check on column {target}",
                }

            try:
                actual_num = float(actual)
                expected_num = float(expected)
                passed = abs(actual_num - expected_num) < 0.001
            except (ValueError, TypeError):
                return {
                    "passed": False,
                    "message": f"Non-numeric values in arithmetic check on column {target}",
                }

            return {
                "passed": passed,
                "message": f"Column {target}C = {actual}, Expected: {expected:.2f}",
            }

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
                passed = str_value.isdigit() or (
                    str_value.startswith("-") and str_value[1:].isdigit()
                )
            elif expected_type == "float":
                try:
                    float(value)
                    passed = True
                except (ValueError, TypeError):
                    passed = False
            elif expected_type == "string_type":
                passed = isinstance(value, str)
            else:
                passed = False

            return {
                "passed": passed,
                "message": f"Column {column}C is {expected_type}: {passed}",
            }

        elif rule_type == "comparison":
            column = rule["column"]
            operator = rule["operator"]
            expected_value = rule["value"]
            actual_value = data.get(column)

            if actual_value is None:
                return {"passed": False, "message": f"Column {column}C is empty"}

            # Try numeric comparison
            try:
                actual_num = float(actual_value)
                expected_num = float(expected_value)

                if operator == "=":
                    passed = abs(actual_num - expected_num) < 0.001
                elif operator == "!=":
                    passed = abs(actual_num - expected_num) > 0.001
                elif operator == ">":
                    passed = actual_num > expected_num
                elif operator == "<":
                    passed = actual_num < expected_num
                elif operator == ">=":
                    passed = actual_num >= expected_num
                elif operator == "<=":
                    passed = actual_num <= expected_num
                else:
                    passed = False
            except (ValueError, TypeError):
                # String comparison
                actual_str = str(actual_value)
                expected_str = str(expected_value)

                if operator == "=":
                    passed = actual_str == expected_str
                elif operator == "!=":
                    passed = actual_str != expected_str
                else:
                    passed = False

            return {
                "passed": passed,
                "message": f"Column {column}C = {actual_value}, Expected {operator} {expected_value}",
            }

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

            return {
                "passed": passed,
                "message": f"Column {column}C {operator} '{pattern}': {passed}",
            }

        elif rule_type == "range":
            column = rule["column"]
            min_val = rule["min"]
            max_val = rule["max"]

            value = data.get(column)

            if value is None:
                return {
                    "passed": False,
                    "message": f"Missing data for range check on column {column}",
                }

            try:
                value_num = float(value)
                passed = min_val <= value_num <= max_val
            except (ValueError, TypeError):
                passed = False

            return {
                "passed": passed,
                "message": f"Column {column}C = {value} in range [{min_val}, {max_val}]: {passed}",
            }

        elif rule_type == "validation":
            column = rule["column"]
            validation = rule["validation"]
            value = data.get(column)

            if validation == "required":
                passed = value is not None and str(value).strip() != ""
            else:
                passed = False

            return {
                "passed": passed,
                "message": f"Column {column}C is required: {passed}",
            }

        return {"passed": False, "message": f"Unknown rule type: {rule_type}"}

    def validate_data(self, data):
        """Validate data against all rules"""
        results = []

        for rule in self.rules:
            result = self.validate_rule(rule, data)
            results.append(
                {"rule": rule, "passed": result["passed"], "message": result["message"]}
            )

        return results
