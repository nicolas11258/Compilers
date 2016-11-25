# goparser.py# -*- coding: utf-8 -*-from ply import yaccfrom errors import errorfrom golex import tokensfrom goast import *precedence = (    ('left', 'LOR'),    ('left', 'LAND'),    ('nonassoc', 'LT', 'LE', 'EQ', 'GT', 'GE', 'NE'),    ('left', 'PLUS', "MINUS"),    ('left', "TIMES", "DIVIDE", "MODULE"),    ('nonassoc', 'LPAREN', 'RPAREN'),    ('right', 'UNARY'),  # operador ficticio para mantener la mas alta prioridad)# ----------------------------------------------------------------------def p_program(p):    '''    program : statements        | empty    '''    p[0] = Program(p[1])def p_statements(p):    '''    statements :  statements statement    '''    p[0] = p[1]    p[0].append(p[2])def p_statements_1(p):    '''    statements :  statement    '''    p[0] = Statements([p[1]])def p_statement(p):    '''    statement :  const_declaration          |  var_declaration          |  extern_declaration          |  function_declaration          |  function_call_statement          |  assign_statement          |  print_statement          |  if_statement          |  while_statement          |  return_statement    '''    p[0] = Statement(p[1])def p_const_declaration(p):    '''    const_declaration : CONST ID ASSIGN expression SEMI    '''    p[0] = ConstDeclaration(p[2],p[4], lineno=p.lineno(2)) # se agregó lineno=p.lineno(2)def p_var_declaration(p):    '''    var_declaration : VAR ID typename SEMI    '''    p[0] = VarDeclaration(p[2], p[3], None, lineno=p.lineno(2))def p_var_declaration_1(p):    '''    var_declaration : VAR ID typename ASSIGN expression SEMI    '''    p[0] = VarDeclaration(p[2], p[3], p[5], lineno=p.lineno(2)) # se agregó lineno=p.lineno(2)def p_extern_declaration(p):    '''    extern_declaration : EXTERN func_prototype SEMI    '''    p[0] = Extern(p[2], lineno=p.lineno(1)) # se agregó lineno=p.lineno(1)def p_func_prototype(p):    '''    func_prototype : FUNC ID LPAREN parameters RPAREN typename    '''    p[0] = FuncPrototype(p[2], p[4], p[6], lineno=p.lineno(1)) # se agregó lineno=p.lineno(1)def p_parameters(p):    '''    parameters : parameters COMMA parm_declaration    '''    p[0] = p[1]    p[0].append(p[3])def p_parameters_1(p):    '''    parameters : parm_declaration           | empty    '''    p[0] = Parameters([p[1]])def p_parm_declaration(p):    '''    parm_declaration : ID typename    '''    p[0] = ParamDecl(p[1], p[2],lineno=p.lineno(1)) # se agrega lineno=p.lineno(1)def p_assign_statement(p):    '''    assign_statement : location ASSIGN expression SEMI    '''    p[0] = AssignmentStatement(p[1], p[3], lineno=p.lineno(2)) # se agregó lineno=p.lineno(2)def p_print_statement(p):    '''    print_statement : PRINT expression SEMI    '''    p[0] = PrintStatement(p[2], lineno=p.lineno(1)) # se agregó lineno=p.lineno(1)def p_expression_unary(p):    '''    expression :  PLUS expression %prec UNARY           |  MINUS expression %prec UNARY           |  LNOT expression %prec UNARY    '''    p[0] = UnaryOp(p[1], p[2], lineno=p.lineno(1))def p_expression_binary(p):    '''    expression :  expression PLUS expression           | expression MINUS expression           | expression TIMES expression           | expression DIVIDE expression           | expression MODULE expression    '''    p[0] = BinaryOp(p[2], p[1], p[3], lineno=p.lineno(2)) # Se agregó 'lineno=p.lineno(2)'def p_expression_relation(p):    '''    expression : expression LE expression            | expression LT expression            | expression EQ expression            | expression NE expression            | expression GE expression            | expression GT expression            | expression LAND expression            | expression LOR expression    '''    p[0] = RelationalOp(p[2], p[1], p[3], lineno=p.lineno(2))def p_expression_group(p):    '''    expression : LPAREN expression RPAREN    '''    p[0] = Group(p[2])# Se renombró la regla 'expression_funcall' a 'function_call_statement'# SEMI token no estaba# El segundo parámetro [2] en FunCall fue cambiado a p[3]def p_function_call_statement(p):    '''    function_call_statement :  ID LPAREN exprlist RPAREN SEMI    '''    p[0] = FunCall(p[1], p[3], lineno=p.lineno(1)) # se anexó lineno=p.lineno(1)def p_if_statement(p):    '''    if_statement : IF expression LBRACE then_if RBRACE    '''    p[0] = IfStatement(p[2], p[4], None, lineno=p.lineno(1)) # se agregó lineno=p.lineno(1)def p_if_else_statement(p):    '''    if_statement : IF expression LBRACE then_if RBRACE ELSE LBRACE then_else RBRACE    '''    p[0] = IfStatement(p[2], p[4], p[8], lineno=p.lineno(1)) # se agregó lineno=p.lineno(1)# se cambio statements por bodydef p_while_statement(p):    '''    while_statement : WHILE expression LBRACE while_body RBRACE    '''    p[0] = WhileStatement(p[2], p[4], lineno=p.lineno(1)) # se agregó lineno=p.lineno(1)def p_expression_location(p):    '''    expression :  location    '''    p[0] = LoadLocation(p[1]) # Se eliminó el segundo argumento -> ,lineno=p.lineno(1)# fue creada y usada la clase ExprLiteraldef p_expression_literal(p):    '''    expression :  literal    '''    p[0] = p[1] # ExprLiteral(p[1]) -> fue removidodef p_exprlist(p):    '''    exprlist :  exprlist COMMA expression    '''    p[0] = p[1]    p[0].append(p[3])def p_exprlist_1(p):    '''    exprlist : expression           | empty    '''    p[0] = ExprList([p[1]])def p_literal(p):    '''    literal : INTEGER_VALUE            | FLOAT_VALUE            | STRING_VALUE            | BOOLEAN_VALUE    '''    p[0] = Literal(p[1],lineno=p.lineno(1))# fue creada y usada la clase Locationdef p_location(p):    '''    location : ID    '''    p[0] = Location(p[1],lineno=p.lineno(1)) # se restaura el objeto Location(p[1]) con un nuevo anexo 'lineno=p.lineno(1)'# fue creada y usada la clase Typenamedef p_typename(p):    '''    typename : ID    '''    p[0] = Typename(p[1],lineno=p.lineno(1))# se hizo uso de la clase Emptydef p_empty(p):    '''    empty    :    '''    p[0] = Empty()# Usted debe implementar el resto de las reglas de la gramatica# a partir de aqui.def p_expression_funcall(p):    '''    expression : ID LPAREN exprlist RPAREN    '''    p[0] = FunCall(p[1],p[3],lineno=p.lineno(1))def p_return_statement(p):    '''    return_statement : RETURN expression SEMI    '''    p[0] = ReturnStatement(p[2], lineno=p.lineno(1)) # se agrega lineno=p.lineno(1)# Se realizó un cambio en la estructura de la regla function_declarationdef p_function_declaration(p):    '''    function_declaration : FUNC ID LPAREN parameters RPAREN typename LBRACE func_body RBRACE    '''    p[0] = FuncDeclaration(p[2],p[4],p[6],p[8],lineno=p.lineno(2))def p_function_declaration_without_type(p):    '''    function_declaration : FUNC ID LPAREN parameters RPAREN empty LBRACE func_body RBRACE    '''    p[0] = FuncDeclaration(p[2],p[4],p[6],p[8],lineno=p.lineno(2))def p_then_if(p):    '''    then_if : statements            | empty    '''    p[0] = ThenIf(p[1])def p_then_else(p):    '''    then_else : statements            | empty    '''    p[0] = ThenElse(p[1])def p_while_body(p):    '''    while_body : statements                |  empty    '''    p[0] = WhileBody(p[1])def p_func_body(p):    '''    func_body : statements                | empty    '''    p[0] = FuncBody(p[1])# ----------------------------------------------------------------------# NO MODIFIQUE## capturar todos los errores.  La siguiente función es llamada si existe# una entrada mala. Vea http://www.dabeaz.com/ply/ply.html#ply_nn31def p_error(p):    if p:        error(p.lineno, "Error de sintaxis de entrada en token '%s'" % p.value)        #assert(None), "Error de sintáxis de entrada en token '%s', error en la línea %s" % (p.value, p.lineno)    else:        error("EOF","Error de sintaxis. No hay mas entrada.")        #assert(None), "Error de sintáxis. No hay más entrada."# ----------------------------------------------------------------------#              NO MODIFIQUE NADA DE AQUI EN ADELANTE# ----------------------------------------------------------------------def make_parser():    parser = yacc.yacc()    return parserif __name__ == '__main__':    import golex    import sys    from errors import subscribe_errors    lexer = golex.make_lexer()    parser = make_parser()    with subscribe_errors(lambda msg: sys.stdout.write(msg+"\n")):        program = parser.parse(open(sys.argv[1]).read())    # Output the resulting parse tree structure    # for depth,node in flatten(program):    #     print("%s%s" % (" "*(4*depth),node))