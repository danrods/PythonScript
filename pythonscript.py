#Daniel Rodrigues
#SBU ID : 109 117 498

import sys
import tpg
import types, traceback


method_table = {}
stack = list()
top = 0

    
def printErr():
    print("DA Helllllllll")



def addStackFrame(frameType=None):
    pushStackFrame(StackFrame(frameType))

def removeStackFrame():
    popStackFrame()

def findStackFrame(ftype):
    global top,stack

    global top, stack
    index = top
    frameType = None

    while(topOfStack > 0):

        index = index - 1
        frameType = stack[index].getType()
        if frameType == ftype: 
            return stack[index]

    return None


def pushStackFrame(frame):
    global top, stack
    
    stack.append(frame)
    top = top + 1

def popStackFrame():
    global top,stack
    value = None

    if(top > 0):
        value = stack.pop(top - 1)
        top = top -1
    else:
        print("Error - Can't pop off an empty stack")
        raise SemanticError("Stack is Empty")

    return value

def peekStackFrame():
    global top, stack

    if(top > 0):
        return stack[top -1]
    else:
        return None 


def getMethod(name):
    return method_table.get(name.getName())

def setMethod(name, value=None):
    print("Setting method",repr(name.getName()),"With value : ",repr(value))
    method_table[name.getName()] = value



def findValue(key):
    global top, stack
    topOfStack = top
    value = None

    while(topOfStack > 0):

        topOfStack = topOfStack - 1
        value = stack[topOfStack].get(key)
        if value is not None: break

    return value

def setValue(key, value):
    global top
    found = False;
    index = top

    while(index > 0):

        index = index - 1
        val = stack[index].get(key)
        if val is not None: 
            found = True
            break

    setValueInFrame(key, value, index if(found) else top - 1)


def setValueInFrame(key, value, frame):
    global stack, top

    if(frame):        
        stack[frame].putValue(key, value)
    else:
        stack[top -1].putValue(key, value)



class SemanticError(Exception):
    """
    This is the class of the exception that is raised when a semantic error
    occurs.
    """

    def  __init__(self, error="SEMANTIC ERROR"):
        self.error = error

# A base class for nodes. Might come in handy in the future.
# These are the nodes of our abstract syntax tree.
#
class Node(object):

    #
    # Executes this node.
    #
    def execute(self):
        raise SemanticError("Execute not implemented");


    def evaluate(self):
        """
        Called on children of Node to evaluate that child.
        """
        raise Exception("Not implemented.")


    def location(self):

        """
        Evaluates this node for a location.
        """

        raise SemanticError("Location not implemented");


class Program(Node):

    def __init__(self):
        print("Creating the program!")
        self.blocks = list()
        addStackFrame()

    def addBlock(self, block):
        self.blocks.append(block)

    def execute(self):

        for i in self.blocks:
            print("Running program!")
            i.execute()



class StackFrame(object):

    def __init__(self, frameType=None):
        self.local_symbols = {}
        self.type=frameType

    def getType(self):
        return self.type

    def get(self, key, default=None):
        return self.local_symbols.get(key, default)

    def putValue(self, key, value=None):
        self.local_symbols[key] = value



# *************************ALL NODE RELATED CLASSES ***************************


class IntegerOperation(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        left, right = evalAndCheck(self) 
        if isString(left, right):
            raise SemanticError()
        return (left, right)


class ExecutableNode(Node):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        #left, right = evalAndCheck(self) 
        #if isString(left, right):
        raise SemanticError("Not implemented")
        #return (left, right)
    def location(self):
        raise SemanticError("Not implemented")

    def execute(self):
        raise SemanticError("Not implemented")


class LocationLiteral(ExecutableNode):

    def __init__(self, locId):
        self.locId = locId
        self.indices = list()

    def addIndices(self, newIndex):
        self.indices.append(newIndex)

    def location(self):
        locId = self.locId
        if(not isinstance(locId,str)): locId = locId.getName()
        if "=" in locId: locId = locId.replace("=","")
        if "!" in locId: locId = locId.replace("!","")
        locId = locId.strip()

        location = locId #Just for returning later
        if(len(self.indices) > 0):
            index = self.indices[len(self.indices) - 1].evaluate()
        else:
            index = -1
        if self.indices:
            location = findValue(locId)
            #location = symbol_table.get(locId)
            for i in range(0, len(self.indices) -1):
                if isinstance(location, list):
                    location = location[i]
                else:
                    raise SemanticError("There are more indices than available dimensions")

        return (location, index) #Don't think this is going to work



class IntLiteral(Node):
    """
    A node representing integer literals.
    """

    def __init__(self, value):
        if "[" in value:
            value.replace("[", "")
        if "]" in value:
            value.replace("[", "")
        self.value = int(value)

    def evaluate(self):
        return self.value


class StrLiteral(Node):

    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.value.replace("\"", "")

class ListLiteral(Node):

    def __init__(self):
        self.List = list()

    def evaluateAsVar(self):
        mList = self.List

        for i in range(0, len(mList)):
            val = mList[i]
            val = val.getName()
            mList[i] = val

        return mList

    def evaluate(self):
        mList = self.List

        temp = list()

        for i in range(0, len(mList)):
            val = mList[i]
            val = val.evaluate()
            temp.append(val)

        return temp

    def append(self, item):
        self.List.append(item)

    def getLength(self):
        return len(self.List)



class ListIndex(Node):

    def __init__(self, left, right):
        self.mList = left
        self.index = right

    def evaluate(self):

        left = self.mList.evaluate()
        right = self.index.evaluate()

        if not(isinstance(left, list) or isinstance(left, str)):
            raise SemanticError()
        if not(isinstance(right, int) or isinstance(right, list)):
            raise SemanticError()
        if (len(left) < abs(right)):
            raise SemanticError()

        return left[right] if (isinstance(left, str)) else left[right].evaluate()


####### Standard Operations ##################
    
class Multiply(IntegerOperation):
    """
    A node representing multiplication.
    """

    def __init__(self, left, right):
        IntegerOperation.__init__(self,left,right)

    def evaluate(self):
        left, right = IntegerOperation.evaluate(self)
        return left * right


class Divide(IntegerOperation):
    """
    A node representing division.
    """

    def __init__(self, left, right):
        IntegerOperation.__init__(self,left,right)

    def evaluate(self):
        left, right = IntegerOperation.evaluate(self)
        if right == 0:
            raise SemanticError()
        return left / right


class Mod(IntegerOperation):
    """
    A node representing division.
    """

    def __init__(self, left, right):
        IntegerOperation.__init__(self,left,right)

    def evaluate(self):
        left, right = IntegerOperation.evaluate(self)
        if right == 0:
            raise SemanticError()
        return left % right


class Addition(Node):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        left, right = evalAndCheck(self)
        return left + right


class Sub(IntegerOperation):

    def __init__(self, left, right):
        IntegerOperation.__init__(self,left,right)

    def evaluate(self):
        left, right = IntegerOperation.evaluate(self)
        return left - right




class XOR(IntegerOperation):

    def __init__(self, left, right):
        IntegerOperation.__init__(self,left,right)

    def evaluate(self):
        left, right = IntegerOperation.evaluate(self)
        return left ^ right





######## Boolean Operations #########





class AND(IntegerOperation):

    def __init__(self, left, right):
        IntegerOperation.__init__(self,left,right)

    def evaluate(self):
        left, right = IntegerOperation.evaluate(self)
        return left and right

class OR(IntegerOperation):

    def __init__(self, left, right):
        IntegerOperation.__init__(self,left,right)

    def evaluate(self):
        left, right = IntegerOperation.evaluate(self)
        return 1 if ((left != 0) or (right != 0)) else 0

class NOT(IntegerOperation):

    def __init__(self, value):
        IntegerOperation.__init__(self,value,None)

    def evaluate(self):
        value, none = IntegerOperation.evaluate(self)
        return 0 if(value != 0) else 1



class EqComparison(IntegerOperation):

    def __init__(self, left, right):
        IntegerOperation.__init__(self,left,right)

    def evaluate(self):
        left, right = IntegerOperation.evaluate(self)
        return 1 if (left == right) else 0

class GtComparison(IntegerOperation):

    def __init__(self, left, right):
        IntegerOperation.__init__(self,left,right)

    def evaluate(self):
        left, right = IntegerOperation.evaluate(self)
        return 1 if (left > right) else 0

class LtComparison(IntegerOperation):

    def __init__(self, left, right):
        IntegerOperation.__init__(self,left,right)

    def evaluate(self):
        left, right = IntegerOperation.evaluate(self)
        return 1 if (left < right) else 0


############### Statements#######################



#
# A node representing access to a variable.
#
class Variable(Node):

    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name
        
    def evaluate(self):
        if(not self.name or self.name is ""): raise SemanticError("Key doesn't exist")
        #val = symbol_table.get(self.name)
        val = findValue(self.name)
        if val is None: 
            raise SemanticError("Variable does not exist")
        return val


class ArrayVariable(Node):

    def __init__(self, arr):
        self.arr = arr
        self.indices =[]

    def addIndex(self, index):
        self.indices.append(index)

    def evaluate(self):
        variableArray = self.arr.evaluate()
        #index = self.indices


        for indice in range(0,len(self.indices)-1):
            index = self.indices[indice].evaluate()
            if index >= 0 and index < len(variableArray):
                variableArray = variableArray[index]
            else:
                raise SemanticError("Array must have accompanying index to fetch value")

        lastIndex = self.indices[len(self.indices) -1].evaluate()
        return variableArray[lastIndex]


class MethodHeader(ExecutableNode):


    def __init__(self):
        print("Created Method")

    def execute(self):
        print("Executing method header")

    def setVariablesBlock(self, variables, block):
        self.variables = variables.evaluateAsVar()
        self.block = block

    def getVariables(self):
        return self.variables

    def getBlock(self):
        return self.block

#
# Class that encapsulates a method
#
class Method(ExecutableNode):

    def __init__(self, name, var):
        self.name = name
        self.boundVariables = var
        #method_table[name] = self

    def bindVariables(self, values):
        self.boundVariables = values
        
    def execute(self):
        return self.evaluate()

    def evaluate(self):
        methodProto = getMethod(self.name)

        boundVariables = self.boundVariables.evaluate()
        variables = methodProto.getVariables()#.evaluateAsVar() #The bound variables is in the method header

        if(len(boundVariables) != len(variables)):
            raise SemanticError("Given ", str(len(boundVariables))," variables, expected ",str(len(variables)))

        addStackFrame(self.name)
        for i,key in enumerate(variables):
            value = boundVariables[i]
            setValue(key, value)
            print("Added Value: ",repr(value)," to key: ",key)
        methodProto.getBlock().execute()
        returnVal = findValue("return")
        removeStackFrame()

        if(returnVal):
            return returnVal
        else:
            raise SemanticError("Error getting return value from method")

   

class Return(ExecutableNode):

    def __init__(self, expression):
        self.expression = expression
        self.methodReturn = "return"

    def execute(self):     
        value = self.expression.evaluate()

        tempStack = list()
        total = 0

        while(peekStackFrame().getType() is None):
            tempStack.append(popStackFrame())
            total = total + 1

        setValue(self.methodReturn, value)

        while(total > 0):
            pushStackFrame(tempStack.pop(total - 1))
            total = total - 1




    
#
#A node representing the block statement.
#
class Block(ExecutableNode):


    def __init__(self):
        self.statements = list()

    def addStatement(self, node):
        self.statements.append(node)

    def execute(self):
        #print("Executing Block statements");
        for stmt in self.statements:
            value = stmt.execute()
            if(findValue("return") > 0):
                break

#
# A node representing the if statement.
#
class If(ExecutableNode):

    def __init__(self, expression, statement):
        self.expression = expression
        self.statement = statement

    def execute(self):
        #print("Executing IF Statement!")
        val = self.expression.evaluate()
        if(val):
            addStackFrame()
            self.statement.execute()
            removeStackFrame()


#
#  A node representing the while statement.
#
class While(ExecutableNode):

    def __init__(self, expression, statement):

        self.expression = expression
        self.statement = statement

    def execute(self):
        addStackFrame()
        while(self.expression.evaluate()):
            self.statement.execute()
        removeStackFrame()


#
#A node representing the assignment statement.
#
class Assign(ExecutableNode):


    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self):
        location,index = self.left.location();
        expression = self.right.evaluate();

        if(index == -1): #It's an ID
            setValue(location, expression)
            #symbol_table[location] = expression
        else: #It's a list
            location[index] = expression
        
        
       # print("Done Assigning ",location," value : ",repr(expression))


#
# A node representing the print statement.
#
class Print(ExecutableNode):

    def __init__(self, expression):
        self.expression = expression

    def execute(self):
        print(repr(self.expression.evaluate()))
  

# *************************END NODE RELATED CLASSES ***************************


def evalAndCheck(obj):
    left = obj.left.evaluate()

    if not(obj.right is None):
        right = obj.right.evaluate()
    else:
        right = None
    
    typeCheck(left, right)
    return (left, right)

def typeCheck(left, right):
    
    returnVal = intCheck(left, right) or strCheck(left, right)
    
    if not(returnVal):
        raise SemanticError()

    return returnVal


def intCheck(left, right):
    if isinstance(left, int):
        if isinstance(right, int):
            return True
        elif (right is None):
            return True
        else:
            return False
 
    return False

def strCheck(left, right):
    if isinstance(left, str):
        if isinstance(right, str):
            return True
        elif (right is None):
            return True
        else:
            return False
    else:
        return False


def isString(left, right):
    return strCheck(left, None) or strCheck(right, None)


#"""
    #token str "\".+\"" StrLiteral;
    #"""

# This is the TPG Parser that is responsible for turning our language into
# an abstract syntax tree.
class Parser(tpg.VerboseParser):
    """

    # Options
    #set lexer_verbose = True
    #set lexer_multiline = True

    #Start Tokens
    token integer: "\-?\d+" IntLiteral;
    token string '\"[^\"]*\"' StrLiteral;
    token varLoc '[A-Za-z][A-Za-z0-9_]*[\s]* (!=|=)[^=]' LocationLiteral;
    #token varLiteral '[A-Za-z][A-Za-z0-9_]*' StrLiteral
    token variable '[A-Za-z][A-Za-z0-9_]*' Variable;
    token arrLocation '[A-Za-z][A-Za-z0-9_]*[\s]*' LocationLiteral;

    separator space: "\s";
    separator spaces: "\s+";


    START/a -> $ a = Program() $
    (block/b $ a.addBlock(b)$ | method/b  
    )+
    ;

    method/a -> $ a = MethodHeader() $
    variable/v  $ setMethod(v, a) $
    tupleBuilder/t block/b  $ a.setVariablesBlock(t,b) $
    ;


    methodCall/a -> variable/v tupleBuilder/b $ a = Method(v, b)  $
                                                
    ;

    block/a -> 
        "\{"      
            statements/a
        "}" 
    ;

    statements/a ->  $ a = Block() $
        (statement/b $ a.addStatement(b) $
        )*
    ;

    statement/a ->

     "if" "\(" expression/e "\)" block/s $ a = If(e, s) $

    | "else" block/a 

    | "while" "\(" expression/e "\)" block/s $ a = While(e, s) $

    | "print\(|Print\(" expression/e "\)" ";" $ a = Print(e) $ 

    | "return" expression/v ";" $ a = Return(v) $

    | var/l expression/r ";" $ a = Assign(l, r) $

    | expression/a ";"

    ;

    var/a -> varLoc/a | arrLoc/a 
    ;


    arrLoc/a -> variable/b $ a = LocationLiteral(b)$
           (index/c  $ a.addIndices(c)$
           )+
        "(=)[^=]"
    ;

    


    arrVariable/a -> variable/b $a = ArrayVariable(b)$
        (index/c  $ a.addIndex(c)$
        )+
    ;


    expression/a -> orOperation/a
    ;

    orOperation/a -> andOperation/a
    ("or" andOperation/b $ a = OR(a,b) $
    )* 
    ;

    andOperation/a -> notOperation/a
    ("and" notOperation/b $ a = AND(a,b) $
    )*
    ;

    notOperation/a -> "not" notOperation/a $ a = NOT(a) $
    | comparison/a 
    ;

    comparison/a -> xor/a
    (
     "==" xor/b $ a = EqComparison(a,b) $
    | ">" xor/b $ a = GtComparison(a,b) $
    | "<" xor/b $ a = LtComparison(a,b) $
    )*
    ;

    xor/a -> addsubtract/a 
    ("xor" addsubtract/b $ a = XOR(a,b) $
    )*
    ;

    addsubtract/a -> multiplydivide/a
    ( "\+" multiplydivide/b $ a = Addition(a, b) $
    | "\-" multiplydivide/b $ a = Sub(a, b) $
    | "\%" multiplydivide/b $ a = Mod(a, b) $
    )*
    ;

    multiplydivide/a -> listIndex/a
    ("\*" listIndex/b $ a = Multiply(a, b) $
    | "/"  listIndex/b $ a = Divide(a, b) $
    )*
    ;

    listIndex/a -> array/a index/b $ a = ListIndex(a,b) $
    | term/a
    ;
    

    term/b ->  "\(" expression/b "\)" | literal/b
    ;

    array/b -> string/b 
    | listBuilder/b;


    index/b -> "\[" expression/b "\]";


    listBuilder/L -> 
    "\["    $ L = ListLiteral() $
    expression/b  $ L.append(b) $
    ("," expression/b $ L.append(b) $
    )*  
    "\]"
    ;

    tupleBuilder/L -> 
    "\("    $ L = ListLiteral() $
    expression/b  $ L.append(b) $
    ("," expression/b $ L.append(b) $
    )*  
    "\)"
    ;
    
    literal/b -> integer/b 
                | string/b 
                | methodCall/b
                | arrVariable/b 
                | variable/b 
                | listBuilder/b ;
    
    """







def main():
    # Make an instance of the parser. This acts like a function.
    parse = Parser()

    # This is the driver code, that reads in lines, deals with errors, and
    # prints the output if no error occurs.

    # Open the file containing the input.
    try:
        mFile = open(sys.argv[1], "r")
    except(IndexError, IOError):
        mFile = open("input.txt", "r")

    buffer=""
    # For each line in f
    for line in mFile:
        try:
            if line == "\n": continue

            buffer +=line

        except Exception as e:
            print(repr(e))

    mFile.close()
    
    try:

            # Try to parse the expression.

            node = parse(buffer)
            
            addStackFrame()
            # Try to get a result.
            result = node.execute()
            removeStackFrame()

           # for i in method_table:
            #    print(repr(i))


        # If an exception is thrown, print the appropriate error.
    except tpg.Error as e:
        print("SYNTAX ERROR")
        traceback.print_exc(file=sys.stdout)
            # Uncomment the next line to re-raise the syntax error,
            # displaying where it occurs. Comment it for submission.
            # raise
            
    except SemanticError as se:
        print("SEMANTIC ERROR")
        print(repr(se))
        traceback.print_exc(file=sys.stdout)
            # Uncomment the next line to re-raise the semantic error,
            # displaying where it occurs. Comment it for submission.
            # raise

    except Exception as e:
        print("Error! : ", e)
        traceback.print_exc(file=sys.stdout)




main()
