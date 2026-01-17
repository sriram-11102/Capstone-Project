# Validation Rule DSL Syntax Guide

This guide describes the syntax for defining file validation rules.

## Basic Layout
*   **Columns** are referenced by their **1-based index** followed by `C`.
    *   Example: `1C` matches the first column, `50C` matches the 50th.
*   **Strings** must be in double quotes: `"Value"`.
*   **Numbers** can be integers (`100`) or decimals (`10.5`).

## Rule Types

### 1. Requirement Check
Check if a column is not empty.
*   **Syntax**: `[Column] REQUIRED`
*   **Example**: `1C REQUIRED`

### 2. Data Type Check
Check the type of data in a column.
*   **Syntax**: `[Column] IS [Type]`
*   **Types**:
    *   `ALPHANUM` (Letters and numbers only)
    *   `NUMERIC` (Any number)
    *   `INTEGER` (Whole numbers)
    *   `FLOAT` (Decimal numbers)
    *   `STRING` (Any text)
*   **Example**: `2C IS ALPHANUM`

### 3. Comparison
Compare a column against a value (Number, String, or another Column).
*   **Syntax**: `[Column] [Operator] [Value]`
*   **Operators**: `=`, `!=`, `>`, `<`, `>=`, `<=`
*   **Examples**:
    *   `3C > 100` (Amount greater than 100)
    *   `2C = "USD"` (Currency equals USD)
    *   `50C > 40C` (Column 50 is greater than Column 40)

### 4. Text Patterns
Check if text matches a specific pattern.
*   **Syntax**: `[Column] [Operator] "Pattern"`
*   **Operators**:
    *   `STARTS_WITH`
    *   `ENDS_WITH`
    *   `CONTAINS`
    *   `NOT_CONTAINS`
    *   `MATCHES` (Regular Expression)
*   **Examples**:
    *   `1C STARTS_WITH "TXN"`
    *   `2C ENDS_WITH ".com"`
    *   `3C MATCHES "(USD|EUR|GBP)"` (One of these currencies)

### 5. Range Check
Check if a number falls within a range (inclusive).
*   **Syntax**: `[Column] BETWEEN [Min] AND [Max]`
*   **Example**: `4C BETWEEN 10 AND 1000`

### 6. Arithmetic Check
Verify calculations across columns.
*   **Syntax**: `[TargetColumn] = [Expression]`
*   **Example**: `5C = 3C + 4C` (Col 5 should equal Col 3 plus Col 4)
