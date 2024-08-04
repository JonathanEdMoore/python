nyctime = input('Please enter current time: ')

def francetime (time):
       # Code goes here
       int_time = int(time)
       if int_time > 23:
            print('Input must be between 0 and 23')
            return
       if int_time < 0:
            print('Input must be between 0 and 23')
            return
       time_in_france = int_time + 6
       if time_in_france > 23:
            time_in_france = time_in_france - 24
       print(time_in_france)

francetime (nyctime)

