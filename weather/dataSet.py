#Class to dave the pertinent data depending on the service type
class DataSet:
    def __init__(self,type,params):
        if(type != 'temps' and type != 'speeds' and type != 'weather'):
            raise ValueError('unknown type in constructor')
        self.type = type
        if type == 'temps' or type == 'weather':
            if (not params.get('temp') or not isinstance(params.get('temp'), float)):
                raise ValueError('invalid or missing temp parameter')
            self.temp = params.get('temp')
        if type == 'speeds' or type == 'weather':
            if (not params.get('north') or not isinstance(params.get('north'), float)):
                raise ValueError('invalid or missing north parameter')
            if (not params.get('west') or not isinstance(params.get('west'), float)):
                raise ValueError('invalid or missing west parameter')
            self.north = params.get('north')
            self.west = params.get('west')
        self.date = params.get('date')

    def getData(self):
        if self.type == 'temps':
            return {'temp':self.temp, 'date':self.date}
        if self.type == 'speeds':
            return {'north':self.north, 'west':self.west, 'date':self.date}
        if self.type == 'weather':
            return {'temp':self.temp, 'north':self.north, 'west':self.west, 'date':self.date}