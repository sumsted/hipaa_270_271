'''
Created on Nov 5, 2010

@author: sumsted

'''

class Hipaa271:
    '''
    Take a HIPAA 271 input buffer from CMS and pull all beneficiaries from it 
    divide into ~HL**20 segments
    pull out values from each segment
    usage:
    set271Buffer() - pass in buffer containing 271 file
    parse() - parse and load up the _beneficiaryList, returns num benes
    getBeneficiaryList() - returns list of dictionary objects
    getQueryResponse() - returns output like HEW
    '''
    _beneficiaryList = []
    _inputBuffer = ''
    _inputSegments = []
    _queryResponseLayout = [
            {'name':'HICN','start':1,'stop':12},
            {'name':'Last Name','start':13,'stop':18},
            {'name':'First Initial','start':19,'stop':19},
            {'name':'Date of Birth','start':20,'stop':27},
            {'name':'Gender','start':28,'stop':28},
            {'name':'SSN','start':29,'stop':37},
            {'name':'Filler','start':38,'stop':99},
            {'name':'Disposition','start':100,'stop':101},
            {'name':'CMS DCN','start':102,'stop':116},
            {'name':'ICN 1','start':117,'stop':146},
            {'name':'ICN 2','start':147,'stop':176},
            {'name':'Filler','start':177,'stop':300}
           ]

    def __init__(self,inputBuffer=None):
        self.set271Buffer(inputBuffer)

    def set271Buffer(self,inputBuffer):
        if inputBuffer:
            self._inputBuffer = inputBuffer
           
    def parse(self):
        # remove CR and divide into segments
        self._inputBuffer = self._inputBuffer.replace('\n','')
        for segment in self._divideIntoList(self._inputBuffer,'~'):
            self._inputSegments.append(self._divideIntoList(segment,'*'))
        
        # walk through each HL 20 segment
        firstHL = True
        beneficiarySegments = []
        for segment in self._inputSegments:
            if self._iVal(segment,0)=='HL' and self._iVal(segment,3)=='20':
                if not firstHL: 
                    beneficiary = self._parseBeneficiary(beneficiarySegments)
                    self._beneficiaryList.append(beneficiary)
                    beneficiarySegments = []
                else:
                    firstHL=False
            if firstHL:
                continue
            beneficiarySegments.append(segment)
        return len(self._beneficiaryList)

    def getBeneficiaryList(self):
        return self._beneficiaryList
 
    def getQueryResponse(self):
        buffer = ''
        for beneficiary in self._beneficiaryList:
            beneficiary['Filler'] = ' '
            buffer += ''.join([beneficiary[item['name']].ljust(item['stop']-item['start']+1) 
                                for item in self._queryResponseLayout])
            buffer += '\n'
        return buffer
    
    def _parseBeneficiary(self,beneficiarySegments):
        beneficiary = {'SSN':'','Last Name':'','First Initial':'',
                       'HICN':'','Date of Birth':'','Gender':'',
                       'Disposition':'01','CMS DCN':'','ICN 1':'','ICN 2':''}
        for segment in beneficiarySegments:
            label = self._iVal(segment,0)
            qualifier = self._iVal(segment,1)
            if label == 'REF' and qualifier == 'IG':
                beneficiary['SSN'] = self._iVal(segment,2)
            if label == 'NM1' and qualifier == 'IL':
                beneficiary['Last Name'] = self._iVal(segment,3)
                beneficiary['First Initial'] = self._iVal(segment,4)
                beneficiary['HICN'] = self._iVal(segment,9)
            if label == 'DMG' and qualifier == 'D8':
                beneficiary['Date of Birth'] = self._iVal(segment,2)
                beneficiary['Gender'] = {'M':'1','F':'2','U':'0'}[self._iVal(segment,3)]
            if label == 'AAA':
                beneficiary['Disposition'] = '51'
            if label == 'REF' and qualifier == 'NQ':
                beneficiary['ICN 1'] = self._iVal(segment,2)
            if label == 'REF' and qualifier == 'EA':
                beneficiary['ICN 2'] = self._iVal(segment,2)
            if label == 'TRN' and qualifier == '1':
                beneficiary['CMS DCN'] = self._iVal(segment,2)              
        return beneficiary
        
    def _iVal(self,segment,item):
        result = ''
        if segment and len(segment) > item:
            result = segment[item].strip()
        return result

    def _divideIntoList(self,input,delimiter):
        resultList = []
        item = ''
        for c in input:
            if c==delimiter:
                resultList.append(item)
                item = ''
            else:
                item += c
        resultList.append(item)
        return resultList

