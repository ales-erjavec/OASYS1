import os

def checkNumber(value, field_name):
    try:
        float(value)
    except ValueError:
        raise Exception(str(field_name) + " is not a number")

    return value

def checkPositiveNumber(value, field_name):
    value = checkNumber(value, field_name)
    if (value < 0): raise Exception(field_name + " should be >= 0")

    return value

def checkStrictlyPositiveNumber(value, field_name):
    value = checkNumber(value, field_name)
    if (value <= 0): raise Exception(field_name + " should be > 0")

    return value

def checkStrictlyPositiveAngle(value, field_name):
    value = checkNumber(value, field_name)
    if value <= 0 or value >= 360: raise Exception(field_name + " should be > 0 and < 360 deg")

    return value

def checkPositiveAngle(value, field_name):
    value = checkNumber(value, field_name)
    if value < 0 or value > 360: raise Exception(field_name + " should be >= 0 and <= 360 deg")

    return value

def checkEmptyString(string, field_name):
    if string is None: raise Exception(field_name + " should not be an empty string")
    if string.strip() == "": raise Exception(field_name + " should not be an empty string")

    return string

def checkFileName(fileName):
    if fileName is None: raise Exception("File name is Empty")
    if fileName.strip() == "": raise Exception("File name is Empty")

    if os.path.isabs(fileName):
        filePath = fileName
    else:
        if fileName.startswith('/'):
            filePath =  os.getcwd() + fileName
        else:
            filePath = os.getcwd() + '/' + fileName

    return filePath

def checkDir(fileName):
    filePath = checkFileName(fileName)

    container_dir = os.path.dirname(filePath)

    if not os.path.exists(container_dir):
        raise Exception("Directory " + container_dir + " not existing")

    return filePath

def checkFile(fileName):
    filePath = checkDir(fileName)

    if not os.path.exists(filePath):
        raise Exception("File " + fileName + " not existing")

    return filePath
