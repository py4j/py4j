'''
Created on Oct 14, 2010

:author: Barthelemy Dagenais
'''
ESCAPE_CHAR = "\\"

# Entry point
ENTRY_POINT_OBJECT_ID = 't'
CONNECTION_PROPERTY_OBJECT_ID = 'c'
STATIC_PREFIX = 'z:'

# JVM
DEFAULT_JVM_ID = 'rj'
DEFAULT_JVM_NAME = 'default'

# Types
INTEGER_TYPE = 'i'
BOOLEAN_TYPE = 'b'
DOUBLE_TYPE = 'd'
STRING_TYPE = 's'
REFERENCE_TYPE = 'r'
ARRAY_TYPE = 't'
SET_TYPE = 'h'
LIST_TYPE = 'l'
MAP_TYPE = 'a'
NULL_TYPE = 'n'
PACKAGE_TYPE = 'p';
CLASS_TYPE = 'c';
METHOD_TYPE = 'm';
NO_MEMBER = 'o';
VOID_TYPE = 'v'
ITERATOR_TYPE = 'g'
PYTHON_PROXY_TYPE = 'f'

# Protocol
END = 'e'
ERROR = 'x'
SUCCESS = 'y'



# Shortcuts
SUCCESS_PACKAGE = SUCCESS + PACKAGE_TYPE
SUCCESS_CLASS = SUCCESS + CLASS_TYPE
CLASS_FQN_START = 2
END_COMMAND_PART = END + '\n'
NO_MEMBER_COMMAND = SUCCESS + NO_MEMBER

# Commands
CALL_COMMAND_NAME = 'c\n'
FIELD_COMMAND_NAME = 'f\n'
CONSTRUCTOR_COMMAND_NAME = 'i\n'
SHUTDOWN_GATEWAY_COMMAND_NAME = 's\n'
LIST_COMMAND_NAME = 'l\n'
REFLECTION_COMMAND_NAME = "r\n"
MEMORY_COMMAND_NAME = "m\n"
HELP_COMMAND_NAME = 'h\n'
ARRAY_COMMAND_NAME = "a\n"
JVMVIEW_COMMAND_NAME = "j\n";


# Array subcommands
ARRAY_GET_SUB_COMMAND_NAME = 'g\n'
ARRAY_SET_SUB_COMMAND_NAME = 's\n'
ARRAY_SLICE_SUB_COMMAND_NAME = 'l\n'
ARRAY_LEN_SUB_COMMAND_NAME = 'e\n'
ARRAY_CREATE_SUB_COMMAND_NAME = 'c\n'

# Reflection subcommands
REFL_GET_UNKNOWN_SUB_COMMAND_NAME = 'u\n'
REFL_GET_MEMBER_SUB_COMMAND_NAME = 'm\n'
    

# List subcommands
LIST_SORT_SUBCOMMAND_NAME = 's\n'
LIST_REVERSE_SUBCOMMAND_NAME = 'r\n'
LIST_SLICE_SUBCOMMAND_NAME = 'l\n'
LIST_CONCAT_SUBCOMMAND_NAME = 'a\n'
LIST_MULT_SUBCOMMAND_NAME = 'm\n'
LIST_IMULT_SUBCOMMAND_NAME = 'i\n'
LIST_COUNT_SUBCOMMAND_NAME = 'f\n'

# Field subcommands
FIELD_GET_SUBCOMMAND_NAME = 'g\n'
FIELD_SET_SUBCOMMAND_NAME = 's\n'

# Memory subcommands
MEMORY_DEL_SUBCOMMAND_NAME = 'd\n'
MEMORY_ATTACH_SUBCOMMAND_NAME = 'a\n'

# Help subcommands
HELP_OBJECT_SUBCOMMAND_NAME = 'o\n'
HELP_CLASS_SUBCOMMAND_NAME = 'c\n'

# JVM subcommands
JVM_CREATE_VIEW_SUB_COMMAND_NAME = 'c\n'
JVM_IMPORT_SUB_COMMAND_NAME = 'i\n'
JVM_SEARCH_SUB_COMMAND_NAME = 's\n'
REMOVE_IMPORT_SUB_COMMAND_NAME = 'r\n'

# Callback specific
PYTHON_PROXY_PREFIX = 'p'
ERROR_RETURN_MESSAGE = ERROR + '\n'

CALL_PROXY_COMMAND_NAME = 'c'
GARBAGE_COLLECT_PROXY_COMMAND_NAME = 'g'

OUTPUT_CONVERTER = {NULL_TYPE: (lambda x, y: None),
              BOOLEAN_TYPE: (lambda value, y: value.lower() == 'true'),
              INTEGER_TYPE: (lambda value, y: int(value)),
              DOUBLE_TYPE: (lambda value, y: float(value)),
              STRING_TYPE: (lambda value, y: unescape_new_line(value)),
              }

INPUT_CONVERTER = []

def escape_new_line(original):
    """Replaces new line characters by a backslash followed by a n.
    
    Backslashes are also escaped by another backslash.
    
    :param original: the string to escape
    
    :rtype: an escaped string
    """
    return original.replace('\\', '\\\\').replace('\r','\\r').replace('\n','\\n')

def unescape_new_line(escaped):
    """Replaces escaped characters by unescaped characters.
    
    For example, double backslashes are replaced by a single backslash.
    
    :param escaped: the escaped string
    
    :rtype: the original string
    """
    escaping = False
    original = ''
    for c in escaped:
        if not escaping:
            if c == ESCAPE_CHAR:
                escaping = True
            else:
                original += c
        else:
            if c == 'n':
                original += '\n'
            elif c == 'r':
                original += '\r'
            else:
                original += c
            escaping = False
            
    return original

    
def is_python_proxy(parameter):
    """Determines whether parameter is a Python Proxy, i.e., it has a Java internal class with an
    implements member.
    :param parameter: the object to check.
    :rtype: True if the parameter is a Python Proxy
    """
    try:
        is_proxy = len(parameter.Java.implements) > 0
    except:
        is_proxy = False
    
    return is_proxy
    
def get_command_part(parameter, python_proxy_pool=None):
    """Converts a Python object into a string representation respecting the Py4J protocol.
    
    For example, the integer `1` is converted to `u'i1'`
    
    :param parameter: the object to convert
    :rtype: the string representing the command part
    """
    command_part = ''
    if parameter == None:
        command_part = NULL_TYPE
    elif isinstance(parameter, bool):
        command_part = BOOLEAN_TYPE + str(parameter)
    elif isinstance(parameter, int) or isinstance(parameter, long):
        command_part = INTEGER_TYPE + str(parameter)
    elif isinstance(parameter, float):
        command_part = DOUBLE_TYPE + str(parameter) 
    elif isinstance(parameter, basestring):
        command_part = STRING_TYPE + escape_new_line(parameter)
    elif is_python_proxy(parameter):
        command_part = PYTHON_PROXY_TYPE + python_proxy_pool.put(parameter)
        for interface in parameter.Java.implements:
            command_part += ';' + interface
    else:
        command_part = REFERENCE_TYPE + parameter._get_object_id()
    
    return command_part + '\n'

def get_return_value(answer, gateway_client, target_id=None, name=None):
    """Converts an answer received from the Java gateway into a Python object.
    
    For example, string representation of integers are converted to Python integer, 
    string representation of objects are converted to JavaObject instances, etc.
    
    :param answer: the string returned by the Java gateway
    :param gateway_client: the gateway client used to communicate with the Java Gateway. Only necessary if the answer is a reference (e.g., object, list, map)
    :param target_id: the name of the object from which the answer comes from (e.g., *object1* in `object1.hello()`). Optional.
    :param name: the name of the member from which the answer comes from (e.g., *hello* in `object1.hello()`). Optional.
    """
    if is_error(answer)[0]:
        if len(answer) > 1:
            raise Py4JError('An error occurred while calling %s%s%s. Trace:\n%s\n' % (target_id, '.', name, unescape_new_line(answer[1:])))
        else:
            raise Py4JError('An error occurred while calling %s%s%s' % (target_id, '.', name))
    else:
        type = answer[1]
        if type == VOID_TYPE:
            return
        else:
            return OUTPUT_CONVERTER[type](answer[2:], gateway_client)
        
def is_error(answer):
    if len(answer) == 0 or answer[0] != SUCCESS:
        return (True, None)
    else:
        return (False, None)

def register_output_converter(output_type, converter):
    global OUTPUT_CONVERTER
    OUTPUT_CONVERTER[output_type] = converter
    
def register_input_converter(converter):
    global INPUT_CONVERTER
    INPUT_CONVERTER.append(converter)

class Py4JError(Exception):
    """Exception thrown when a problem occurs with Py4J."""
    pass



# For circular dependencies
# Purists should close their eyes
