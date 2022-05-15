import os, enum;
from abc import ABC, abstractmethod
import sys
import traceback, inspect, json

        
class File:
    dir = None
    fileName = None
    fullyQualified = None
    def __init__(self, dir, fileName):
        self.dir = dir
        self.fileName = fileName
        self.fullyQualified = dir + '/' + fileName;
        
def addFiles(fileList, directory):
   for root, dirs, files in os.walk(directory):
        for file in files:
            fileList.append(File(root, file))
        for subdir in dirs:
            addFiles(fileList, subdir);
            
    
class Result(enum.Enum):
    failedMatch = 0           #didn't match - reset to zero
    matchedProgress = 1       #all requirements met - move on to the next requirement 
    oneOfManyMatches = 2      #Data gathered - keep on feeding me more lines
    endOfSet = 3              #contiguous set has ended - re-analyze this line
    gameSetMatch = 4          #Found end of data set - go spit out results
    lookForExtraComment = 5
"""
    define an array of matching patterns
    Params:
    1 - Index to expect parameter 2
    2 - Space delimited match string
    3 - Data array index to capture
 - Populated value - starts as None (null)
"""
class Requirement(ABC):
    @abstractmethod
    def testline(self, line):
        pass
    @abstractmethod
    def reset(self):
        pass
    @abstractmethod
    def addResults(self, dictionary):
        pass
class Splicer(Requirement):
    def __init__(self, matchIdx, matchValue, captureIndex, foundValue):
        self.matchIdx = matchIdx
        self.matchValue = matchValue
        self.captureIndex = captureIndex
        self.foundValue = foundValue
    def addResults(self, dictionary):
        dictionary[self.matchValue] = self.foundValue;
    @abstractmethod
    def getSpliceChar(self):
        pass
    def testline(self, line):
        sp = line.split(self.getSpliceChar())
        if (sp is not None and 
            len(sp) > self.matchIdx and 
            len(sp) > self.captureIndex and 
            self.matchValue == sp[self.matchIdx]):
            self.foundValue = sp[self.captureIndex].strip()
            return Result.matchedProgress
        return Result.failedMatch
    def reset(self):
        self.foundValue = None
        
class SpaceSplicer(Splicer):
    def getSpliceChar(self):
        return ' '

class ColonSplicer(Splicer): #Ouch?
    def getSpliceChar(self):
        return ':'
    def testline(self, line):
        retVal = super().testline(line)
        if (retVal == Result.matchedProgress):
            if (self.matchValue == 'Date'):
                i = line.index('Date:')
                self.foundValue = line[i+5::]
                self.foundValue = line.strip()
        return retVal
    
class Blank(Requirement):
    def reset(self):
        return;
    def addResults(self, dictionary):
        return;
    def testline(self, line):
        if (line is None):
            print('Not sure what to: do with None-zies')
        elif (len(line.strip()) == 0):
            #blank line!
            return Result.matchedProgress
        return Result.failedMatch
class Comment(Requirement):
    def reset(self):
        self.comment = None;
    def addResults(self, dictionary):
        return;
    def testline(self, line):
        self.comment = line.strip()
        return Result.matchedProgress
    
class FileInfo:
    def __init__(self, extension):
        self.extension = extension
        self.textLineCount = 0;
        self.binByteCount= 0;
        self.isBinary = False
        self.inserts = 0
        self.deletes = 0
        self.occurrences = 0
def removeEmptyStrings(array):
    retVal = []
    for k in array:
        if (len(k) > 0):
            retVal.append(k)
    return retVal
def addIntValue(dictionary, key, intval):
    curVal = dictionary.get(key)
    if (curVal is None):
        curVal = 0
    dictionary[key] = curVal + intval;
class FileCommit(Requirement):
    def __init__(self):
        self.reset()
    def reset(self):
        self.extensionDic = {}
        self.foundOneOrMoreLines = False
    def addResults(self, dictionary):
        fileTypes = dictionary.get('fileTypes')
        if (fileTypes is None):
            fileTypes = {}
            dictionary['fileTypes'] = fileTypes;
        for key in self.extensionDic:
            fi = self.extensionDic.get(key)
            sumDic = fileTypes.get(fi.extension)
            if (sumDic is None):
                sumDic = {}
                fileTypes[fi.extension] = sumDic
            addIntValue(sumDic, 'textLineCount', fi.textLineCount)
            addIntValue(sumDic, 'binByteCount', fi.binByteCount)
            addIntValue(sumDic, 'inserts', fi.inserts)
            addIntValue(sumDic, 'deletes', fi.deletes)
            addIntValue(sumDic, 'occurrences', fi.occurrences)
            
    def getExt(self, ext):
        fi = self.extensionDic.get(ext)
        if (fi is None):
            fi = FileInfo(ext)
            self.extensionDic[ext] = fi
        return fi
    @abstractmethod
    def split(self, line):
        pass
    @abstractmethod
    def processStatistics(self, line, file_info, extension):
        pass
    
        
    def testline(self, line):
#        print('Testing for commit line: "'+line+'"')
        fileNamePortion, statsPortion = self.split(line)
        validData = False;
        if (fileNamePortion is not None and statsPortion is not None):
            fileNameArray = fileNamePortion.split('/');
            fileName = fileNameArray[len(fileNameArray)-1];
#            print('Filename spliced into:'+fileName)
            dotSplit = fileName.split('.')
            ext = 'noexttext'
            if (fileName.startswith('.') == False and len(dotSplit) > 1):
                ext = dotSplit[len(dotSplit)-1].strip() #last element (e.g. '.txt')
                ext = removeEmptyStrings(ext.split('}'))[0]
            fi = self.getExt(ext)
            fi.occurrences += 1
            validData = self.processStatistics(statsPortion, fi, ext)

        returnVal = Result.endOfSet
        if (validData == True):
            self.foundOneOrMoreLines = True
#            print('Returning '+str(Result.oneOfManyMatches))
            returnVal = Result.oneOfManyMatches
        elif (self.foundOneOrMoreLines == False):
            returnVal = Result.lookForExtraComment
                
        return returnVal
    
class StatFileCommit(FileCommit):
    def split(self, line):
        sp = line.split('|')
        if (len(sp) < 2):
            return None, None
        return sp[0], sp[1]

    def processStatistics(self, line, fi, ext):
        validData = False;
        size = removeEmptyStrings(line.split(' '))        
#            print('Size element array is:'+str(size))
        if (size[0].startswith('Bin')): #binary file - handle separately
            if (ext == 'noexttext'):
                fi.occurrences -= 1
                ext = 'noextbin'
                fi = self.getExt(ext)
                fi.occurrences += 1
            if (len(size) > 1):
                sizeBefore = int(size[1]) if size[1].isnumeric() else -1
                sizeAfter = int(size[3]) if size[3].isnumeric() else -1
                if (sizeBefore >= 0 and sizeAfter >= 0):
                    validData = True
                    fi.isBinary = True
                    fi.binByteCount += (sizeAfter - sizeBefore)
            else:
                validData = True
                fi.isBinary = True
        elif (size[0].isnumeric and len(size[0]) > 0):
            fi.isBinary = False
            try:
              lc = int(size[0])
              fi.textLineCount += lc
              plusCount = 0
              minusCount = 0
              if (lc < 1 and len(size) < 2):
                  #all done here
                  validData = True
              else:
                  plus = size[1].split('+')
                  for p in plus:
                      if (len(p) == 0):
                          plusCount += 1
                      else:
                          mi = len(p.split('-')) - 1
                          minusCount += mi
                  if (plusCount > 0 or minusCount > 0):
                      validData = True
                      fi.inserts = int(fi.textLineCount * ((plusCount * 1.0) / (plusCount + minusCount)))
                      fi.deletes = fi.textLineCount - fi.inserts
                  else:
                      print('No bueno!')
            except:
              print('Exception encountered parsing:', size[0])
        return validData
                        
class NumStatFileCommit(FileCommit):
    def split(self, line):
        try:
            chunks = line.split(' ')
            file_name_portion = chunks[2]
            stats_portion = chunks[0]+' '+chunks[1]
            if (chunks[0].isnumeric() or chunks[0] == '-') and (chunks[1].isnumeric() or chunks[0] == '-'):
                return file_name_portion, stats_portion
        except:
            pass
        return None, None
    def processStatistics(self, line, fi, ext):
        print('processStatistics',line, fi, ext)
        return False
    
        
class Summary(Requirement):
    def __init__(self):
        self.reset()
    def reset(self):
        self.junk = ''
        self.totals = {}
    def testline(self, line):
        #print('Testing for Summary line ('+str(line)+')')
        sp = line.split(',')
        for elem in sp:
            spaceDelim = removeEmptyStrings(elem.split(' '))
            if (len(spaceDelim) > 1):
                self.totals[spaceDelim[1]] = spaceDelim[0]
            else:
                print('ERROR - Summary line should have comma-separated change and insertion totals:'+line)
        return Result.gameSetMatch
    def addResults(self, dictionary):
        dictionary.update(self.totals)

class RequirementSet:
    def processDocument(self, multiLineString):
        for line in multiLineString.splitlines():
            self.testline(line)

    def getReqArray(self):
        return self.reqArray;
    @abstractmethod
    def setup_requirements(self):
        pass
    
    def __init__(self):
        self.reqArray = []
        self.setup_requirements()
        self.reqIndex = 0
        self.dataMatchesFound = 0
        self.indexErrorDic = {}
        self.resultArray = []
        self.reset()
    def reset(self):
        self.reqIndex = 0;
        self.dataMatchesFound = 0;
        self.resultDictionary = {}
        for req in self.getReqArray():
            req.reset();
    def processResult(self, line, rslt):
#        if (rslt != Result.failedMatch):
#            print('Processing['+str(self.reqIndex)+']: '+str(rslt));
        if (rslt == Result.failedMatch):
            self.reset();
            self.reqIndex = 0;
        elif (rslt == Result.matchedProgress):
            self.reqIndex += 1
            if (self.reqIndex >= len(self.reqArray)):
                print('ERROR - Last element of RequirementSet cannot return Result.matchedProgress')
                self.reset()
                self.reqIndex = 0
        elif (rslt == Result.oneOfManyMatches):
            #Just keep reading until done
            self.dataMatchesFound += 1
#            print('Just one of many matches ('+str(self.dataMatchesFound)+' total)')
        elif (rslt == Result.endOfSet):
            self.reqIndex += 1
            self.testline(line)
        elif (rslt == Result.gameSetMatch):
#            print('Game set match!')
            for req in self.reqArray:
                req.addResults(self.resultDictionary)
            self.resultArray.append(self.resultDictionary.copy())
            self.reset()
        elif (rslt == Result.lookForExtraComment):
            self.reqIndex = 4 #Go back to the stage that
            self.testline(line)
        else:
            self.reqIndex = 0
            cnt = self.indexErrorDic.get(self.reqIndex)
            if (cnt is None):
                cnt = 0;
                print('ERROR - Unknown result type from requirement index: '+str(self.reqIndex))
            cnt += 1;
            self.indexErrorDic[self.reqIndex] = cnt;

    def testline(self, line):
        if (self.reqIndex >= len(self.reqArray)):
            print('ERROR - RequirementIndex out of range!')
            self.reset();
            self.reqIndex = 0;
            sys.exit()
        else:
            self.processResult(line, self.reqArray[self.reqIndex].testline(line))
            

        
                        
class StatRequirementSet(RequirementSet):
    def setup_requirements(self):
        reqArray = super().getReqArray()
        reqArray.append( SpaceSplicer(0, 'commit', 1, None) )
        reqArray.append( ColonSplicer(0, 'Author', 1, None) )
        reqArray.append( ColonSplicer(0, 'Date', 1, None) )
        reqArray.append( Blank() )
        reqArray.append( Comment() )
        reqArray.append( Blank() )
        reqArray.append( StatFileCommit() )
        reqArray.append( Summary() )
    def __init__(self):
        super().__init__()
        
class NumstatRequirementSet(RequirementSet):        
    def setup_requirements(self):
        reqArray = super().getReqArray()
        reqArray.append( SpaceSplicer(0, 'commit', 1, None) )
        reqArray.append( ColonSplicer(0, 'Author', 1, None) )
        reqArray.append( ColonSplicer(0, 'Date', 1, None) )
        reqArray.append( Blank() )
        reqArray.append( Comment() )
        reqArray.append( Blank() )
        reqArray.append( NumStatFileCommit() )
    def __init__(self):
        super().__init__()

