# goast.py# -*- coding: utf-8 -*-'''Objetos Arbol de Sintaxis Abstracto (AST - Abstract Syntax Tree).Este archivo define las clases para los diferentes tipos de nodos delárbol de sintaxis abstracto.  Durante el análisis sintático, se debecrear estos nodos y conectarlos.  En general, usted tendrá diferentesnodos AST para cada tipo de regla gramatical.  Algunos ejemplos denodos AST pueden ser encontrados al comienzo del archivo.  Usted deberáañadir más.'''# NO MODIFICARclass AST(object):    '''    Clase base para todos los nodos del AST.  Cada nodo se espera    definir el atributo _fields el cual enumera los nombres de los    atributos almacenados.  El método a continuación __init__() toma    argumentos posicionales y los asigna a los campos apropiados.    Cualquier argumento adicional especificado como keywords son    también asignados.    '''    _fields = []    def __init__(self,*args,**kwargs):        assert len(args) == len(self._fields)        for name,value in zip(self._fields,args):            setattr(self,name,value)        # Asigna argumentos adicionales (keywords) si se suministran        for name,value in kwargs.items():            setattr(self,name,value)    def pprint(self):        for depth, node in flatten(self):            print("%s%s" % (" "*(4*depth),node))def validate_fields(**fields):    def validator(cls):        old_init = cls.__init__        def __init__(self, *args, **kwargs):            old_init(self, *args, **kwargs)            for field,expected_type in fields.items():                assert isinstance(getattr(self, field), expected_type)        cls.__init__ = __init__        return cls    return validator# ----------------------------------------------------------------------# Nodos AST especificos## Para cada nodo es necesario definir una clase y añadir la especificación# del apropiado _fields = [] que indique que campos deben ser almacenados.# A modo de ejemplo, para un operador binario es posible almacenar el# operador, la expresión izquierda y derecha, como esto:##    class Binop(AST):#        _fields = ['op','left','right']# ----------------------------------------------------------------------# Unos pocos nodos ejemplosclass PrintStatement(AST):    '''    print expression ;    '''    _fields = ['expr']class Literal(AST):    '''    Un valor constante como 2, 2.5, o "dos"    '''    _fields = ['value']class Program(AST): # No usado originalmente    _fields = ['program']@validate_fields(statements=list)class Statements(AST):    _fields = ['statements']    def append(self,e):        self.statements.append(e)class Statement(AST):    _fields = ['statement']class Extern(AST):    _fields = ['func_prototype']class FuncPrototype(AST):    _fields = ['id', 'params', 'typename']@validate_fields(param_decls=list)class Parameters(AST):    _fields = ['param_decls']    def append(self,e):        self.param_decls.append(e)class ParamDecl(AST):    _fields = ['id', 'typename']class AssignmentStatement(AST):    _fields = ['location', 'value']class ConstDeclaration(AST):    _fields = ['id', 'value']class VarDeclaration(AST):    _fields = ['id', 'typename', 'value']class IfStatement(AST):    _fields = ['condition', 'then_b', 'else_b']class WhileStatement(AST):    _fields = ['condition', 'body']class LoadLocation(AST):    _fields = ['name']class StoreVar(AST): # No usado    _fields = ['name']class UnaryOp(AST):    _fields = ['op', 'left']class BinaryOp(AST):    _fields = ['op', 'left', 'right']class RelationalOp(AST):    _fields = ['op', 'left', 'right']class Group(AST):    _fields = ['expression']class FunCall(AST):    _fields = ['id', 'params']class ExprList(AST):    _fields = ['expressions']    def append(self, e):        self.expressions.append(e)class Empty(AST): # No usado    _fields = []# Usted deberá añadir mas nodos aquí.  Algunos nodos sugeridos son# BinaryOperator, UnaryOperator, ConstDeclaration, VarDeclaration,# AssignmentStatement, etc...class Func_declaration(AST):    _fields = ['func_prototype', 'body']class Expression_array(AST):    _fields = ['name', 'expression']class ParamDeclArray(AST):    _fields = ['id','typename','value']class AssignmentStatementArray(AST):    _fields = ['name','value','expression']class ArrayDeclaration(AST):    _fields = ['id','typename','amount']class ReturnStatement(AST):    _fields = ['expression']class ThenIf(AST):    _fields = ['statements']class ThenElse(AST):    _fields = ['statements']class Location(AST):    _fields = ['id']class ExprLiteral(AST):    _fields = ['value']class SpecialLiteralArray(AST):    _fields = ['amount']# ----------------------------------------------------------------------#                  NO MODIFIQUE NADA AQUI ABAJO# ----------------------------------------------------------------------# Las clase siguientes para visitar y reescribir el AST son tomadas# desde el módulo ast de python .# NO MODIFIQUEclass NodeVisitor(object):    '''    Clase para visitar nodos del árbol de sintaxis.  Se modeló a partir    de una clase similar en la librería estándar ast.NodeVisitor.  Para    cada nodo, el método visit(node) llama un método visit_NodeName(node)    el cual debe ser implementado en la subclase.  El método genérico    generic_visit() es llamado para todos los nodos donde no hay coincidencia    con el método visit_NodeName().    Es es un ejemplo de un visitante que examina operadores binarios:        class VisitOps(NodeVisitor):            visit_Binop(self,node):                print("Operador binario", node.op)                self.visit(node.left)                self.visit(node.right)            visit_Unaryop(self,node):                print("Operador unario", node.op)                self.visit(node.expr)        tree = parse(txt)        VisitOps().visit(tree)    '''    def visit(self,node):        '''        Ejecuta un método de la forma visit_NodeName(node) donde        NodeName es el nombre de la clase de un nodo particular.        '''        if node:            method = 'visit_' + node.__class__.__name__            visitor = getattr(self, method, self.generic_visit)            return visitor(node)        else:            return None    def generic_visit(self,node):        '''        Método ejecutado si no se encuentra médodo aplicable visit_.        Este examina el nodo para ver si tiene _fields, es una lista,        o puede ser recorrido completamente.        '''        print node.__class__.__name__        for field in getattr(node,"_fields"):            value = getattr(node,field,None)            if isinstance(value, list):                for item in value:                    if isinstance(item,AST):                        self.visit(item)            elif isinstance(value, AST):                self.visit(value)# ---------------------- Clase base dot visitor ----------------------class DotVisitor(NodeVisitor):    def __init__(self):        self.dot = 'digraph AST {\n'        self.id = 0        self.st = []    def __repr__(self):        return self.dot + '}'    def set_id_node(self):        self.id += 1        return 'n%02d' % self.id    def visit_Program(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Program",shape=tripleoctagon]\n'        self.visit(node.program)        # El for crea el vínculo entre el nodo principal program y cada hijo statement de la lista statements        for branch in self.st:            self.dot += '\t' + id_node + ' -> '+ branch + '\n'        self.st.append(id_node)        return    # --- nodos statements ---    def visit_ConstDeclaration(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Const\\nid : %s",shape=diamond]\n'% node.id        self.visit(node.value)        left = self.st.pop()        self.dot += '\t' + id_node + ' -> '+ left + '\n'        self.st.append(id_node)        return    def visit_VarDeclaration(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Variable\\nid : %s\\ntipo : %s",shape=diamond]\n'% (node.id,node.typename)        if node.value != None:            self.visit(node.value)            left = self.st.pop()            self.dot += '\t' + id_node + ' -> ' + left + '\n'        self.st.append(id_node)        return    def visit_ArrayDeclaration(self,node): # nodo hoja        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Array\\nid : %s\\ntype : %s\\namount : %s",shape=circle]\n'% (node.id,node.typename,node.amount)        self.st.append(id_node)        return    def visit_Extern(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Extern",shape=diamond]\n'        self.visit(node.func_prototype)        left = self.st.pop()        self.dot += '\t' + id_node + ' -> ' + left + '\n'        self.st.append(id_node)        return    def visit_Func_declaration(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Func declaration",shape=diamond]\n'        self.visit(node.func_prototype)        self.visit(node.body)        size_body = len(node.body.statements) # Cantidad de statements en el cuerpo de la función        for branch in range(0,size_body): # Recorre cada statement del cuerpo de la función            child = self.st.pop()            self.dot += '\t' + id_node + ' -> ' + child + '\n'        left = self.st.pop() # finalmente obtiene el nodo func_prototype        self.dot += '\t' + id_node + ' -> ' + left + '\n'        self.st.append(id_node)        return    def visit_FunCall(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Func call\\nid : %s",shape=diamond]\n'% node.id        self.visit(node.params)        left = self.st.pop()        self.dot += '\t' + id_node + ' -> ' + left + '\n'        self.st.append(id_node)        return    def visit_AssignmentStatement(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "=",shape=diamond]\n'        self.visit(node.location)        self.visit(node.value)        right = self.st.pop()        left = self.st.pop()        self.dot += '\t' + id_node + ' -> ' + left + '\n'        self.dot += '\t' + id_node + ' -> ' + right + '\n'        self.st.append(id_node)        return    def visit_PrintStatement(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Print",shape=diamond]\n'        self.visit(node.expr)        left = self.st.pop()        self.dot += '\t' + id_node + ' -> ' + left + '\n'        self.st.append(id_node)        return    def visit_IfStatement(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "If",shape=diamond]\n'        self.visit(node.condition)        self.visit(node.then_b)        self.visit(node.else_b)        if node.else_b != None: # Si if statement tiene else, conecta el nodo else            child_else = self.st.pop()            self.dot += '\t' + id_node + ' -> ' + child_else + '\n'        child_then = self.st.pop() # Conecta con el nodo then        self.dot += '\t' + id_node + ' -> ' + child_then + '\n'        child_condition = self.st.pop() # Conecta con el nodo condition        self.dot += '\t' + id_node + ' -> ' + child_condition + '\n'        self.st.append(id_node)        return    def visit_WhileStatement(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "While",shape=diamond]\n'        self.visit(node.condition)        self.visit(node.body)        size_body = len(node.body.statements) # va por cada statament del cuerpo del while        for branch in range(0,size_body):            child_statement = self.st.pop()            self.dot += '\t' + id_node + ' -> ' + child_statement + '\n'        child_condition = self.st.pop() # finalmente por su nodo condicion        self.dot += '\t' + id_node + ' -> ' + child_condition + '\n'        self.st.append(id_node)        return    def visit_ReturnStatement(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Return",shape=diamond]\n'        self.visit(node.expression)        left = self.st.pop()        self.dot += '\t' + id_node + ' -> ' + left + '\n'        self.st.append(id_node)        return    # --- fin nodos statements ---

    # --- nodos expressions ---
    def visit_UnaryOp(self,node):
        id_node = self.set_id_node()
        self.dot += '\t' + id_node + ' [label= "Unary op\\noperator : %s",shape=box]\n'% node.op
        self.visit(node.left)
        left = self.st.pop()
        self.dot += '\t' + id_node + ' -> ' + left + '\n'
        self.st.append(id_node)

    def visit_BinaryOp(self,node):
        id_node = self.set_id_node()
        self.dot += '\t' + id_node + ' [label= "Binary op\\noperator : %s",shape=box]\n'% node.op
        self.visit(node.left)
        self.visit(node.right)
        right = self.st.pop()
        left = self.st.pop()
        self.dot += '\t' + id_node + ' -> ' + left + '\n'
        self.dot += '\t' + id_node + ' -> ' + right + '\n'
        self.st.append(id_node)
        return

    def visit_RelationalOp(self,node):
        id_node = self.set_id_node()
        self.dot += '\t' + id_node + ' [label= "Relational op\\noperator : %s",shape=box]\n'% node.op
        self.visit(node.left)
        self.visit(node.right)
        right = self.st.pop()
        left = self.st.pop()
        self.dot += '\t' + id_node + ' -> ' + left + '\n'
        self.dot += '\t' + id_node + ' -> ' + right + '\n'
        self.st.append(id_node)
        return

    def visit_Group(self,node):
        id_node = self.set_id_node()
        self.dot += '\t' + id_node + ' [label= "Parenthesis",shape=box]\n'
        self.visit(node.expression)
        left = self.st.pop()
        self.dot += '\t' + id_node + ' -> ' + left + '\n'
        self.st.append(id_node)
        return

    def visit_LoadLocation(self,node):
        id_node = self.set_id_node()
        self.dot += '\t' + id_node + ' [label= "Load location",shape=box]\n'
        self.visit(node.name)
        left = self.st.pop()
        self.dot += '\t' + id_node + ' -> ' + left + '\n'
        self.st.append(id_node)
        return

    def visit_ExprLiteral(self,node):
        id_node = self.set_id_node()
        self.dot += '\t' + id_node + ' [label= "Expr literal",shape=box]\n'
        self.visit(node.value)
        left = self.st.pop()
        self.dot += '\t' + id_node + ' -> ' + left + '\n'
        self.st.append(id_node)
        return

    def visit_Expression_array(self,node):
        id_node = self.set_id_node()
        self.dot += '\t' + id_node + ' [label= "Expr array",shape=box]\n'
        self.visit(node.name)
        self.visit(node.expression)
        right = self.st.pop()
        left = self.st.pop()
        self.dot += '\t' + id_node + ' -> ' + left + '\n'
        self.dot += '\t' + id_node + ' -> ' + right + '\n'
        self.st.append(id_node)
        return

    def visit_ExprList(self,node):
        id_node = self.set_id_node()
        self.dot += '\t' + id_node + ' [label= "Parameters func call",shape=box]\n'
        # El for hace posible la visita nodo por nodo de una lista de nodos
        # donde cada nodo es una 'expression' qué coincide con algún parámetro de la función en llamada
        for param in node.expressions:
            self.visit(param)
            child_param = self.st.pop()
            self.dot += '\t' + id_node + ' -> ' + child_param + '\n'
        self.st.append(id_node)
        return
    # --- fin nodos expressions ---

    # --- nodos hojas ---
    def visit_Location(self,node):
        id_node = self.set_id_node()
        self.dot += '\t' + id_node + ' [label= "Location\\nid : %s",shape=circle]\n'% node.id
        self.st.append(id_node)
        return

    def visit_Literal(self,node):
        id_node = self.set_id_node()
        self.dot += '\t' + id_node + ' [label= "Literal\\nvalue : %s",shape=circle]\n'% node.value
        self.st.append(id_node)
        return

    def visit_ParamDecl(self,node):
        id_node = self.set_id_node()
        self.dot += '\t' + id_node + ' [label= "Parameter\\nid : %s\\ntypename : %s",shape=circle]\n'% (node.id,node.typename)
        self.st.append(id_node)
        return

    def visit_SpecialLiteralArray(self,node):
        id_node = self.set_id_node()
        self.dot += '\t' + id_node + ' [label= "Literal array\\nReserved amount : %s",shape=circle]\n'% str(node.amount)
        self.st.append(id_node)
        return
    # --- fin nodos hojas ---
    # --- otros nodos ---    def visit_FuncPrototype(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Func prototype\\nid : %s\\nreturn type : %s",shape=box]\n'% (node.id,node.typename)        self.visit(node.params)        left = self.st.pop()        self.dot += '\t' + id_node + ' -> ' + left + '\n'        self.st.append(id_node)        return    def visit_Parameters(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Parameters",shape=box]\n'        for param in node.param_decls:            self.visit(param)            id_child_param = self.st.pop()            self.dot += '\t' + id_node + ' -> ' + id_child_param + '\n'        self.st.append(id_node)        return    def visit_AssignmentStatementArray(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Assignment array",shape=box]\n'        self.visit(node.name)        self.visit(node.value)        self.visit(node.expression)        id_node_expression = self.st.pop()        id_node_value = self.st.pop()        id_node_name = self.st.pop()        self.dot += '\t' + id_node + ' -> '+ id_node_name + '\n'        self.dot += '\t' + id_node + ' -> '+ id_node_value + '\n'        self.dot += '\t' + id_node + ' -> '+ id_node_expression + '\n'        self.st.append(id_node)        return    def visit_ThenIf(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Then",shape=box]\n'        self.visit(node.statements)        size_body = len(node.statements.statements)        for branch in range(0,size_body):            id_child_statement = self.st.pop()            self.dot += '\t' + id_node + ' -> ' + id_child_statement + '\n'        self.st.append(id_node)        return    def visit_ThenElse(self,node):        id_node = self.set_id_node()        self.dot += '\t' + id_node + ' [label= "Else",shape=box]\n'        self.visit(node.statements)        size_body_else = len(node.statements.statements)        for branch in range(0,size_body_else):            id_child_else = self.st.pop()            self.dot += '\t' + id_node + ' -> ' + id_child_else + '\n'        self.st.append(id_node)        return    def visit_ParamDeclArray(self,node):        id_node = self.set_id_node()        self.visit(node.value)        self.dot += '\t' + id_node + ' [label= "Array parameter\\nid : %s\\ntypename : %s",shape=circle]\n'%(node.id,node.typename)        left = self.st.pop()        self.dot += '\t' + id_node + ' -> '+ left + '\n'        self.st.append(id_node)        return    # --- fin otros nodos ---#------------------------------------------------------------------# NO MODIFICARclass NodeTransformer(NodeVisitor):    '''    Clase que permite que los nodos del arbol de sintraxis sean    reemplazados/reescritos.  Esto es determinado por el valor retornado    de varias funciones visit_().  Si el valor retornado es None, un    nodo es borrado. Si se retorna otro valor, reemplaza el nodo    original.    El uso principal de esta clase es en el código que deseamos aplicar    transformaciones al arbol de sintaxis.  Por ejemplo, ciertas optimizaciones    del compilador o ciertas reescrituras de pasos anteriores a la generación    de código.    '''    def generic_visit(self,node):        for field in getattr(node,"_fields"):            value = getattr(node,field,None)            if isinstance(value,list):                newvalues = []                for item in value:                    if isinstance(item,AST):                        newnode = self.visit(item)                        if newnode is not None:                            newvalues.append(newnode)                    else:                        newvalues.append(n)                value[:] = newvalues            elif isinstance(value,AST):                newnode = self.visit(value)                if newnode is None:                    delattr(node,field)                else:                    setattr(node,field,newnode)        return node# NO MODIFICARdef flatten(top):    '''    Aplana el arbol de sintaxis dentro de una lista para efectos    de depuración y pruebas.  Este retorna una lista de tuplas de    la forma (depth, node) donde depth es un entero representando    la profundidad del arból de sintaxis y node es un node AST    asociado.    '''    class Flattener(NodeVisitor):        def __init__(self):            self.depth = 0            self.nodes = []        def generic_visit(self,node):            self.nodes.append((self.depth,node))            self.depth += 1            NodeVisitor.generic_visit(self,node)            self.depth -= 1    d = Flattener()    d.visit(top)    return d.nodes