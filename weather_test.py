import os
from pyowm.owm import OWM
from pyowm.weatherapi25 import one_call
import elevenlabs
from elevenlabs.api import User, Voice, Models


def get_current_weather(loc=os.getenv('GEO_LOCATION')):

    owm = OWM(os.getenv('OWM_API_KEY'))
    mgr = owm.weather_manager()
    obs = mgr.weather_at_place(loc)
    print(obs.to_dict()['weather'])

def check_loc(city_str):
    owm = OWM(os.getenv('OWM_API_KEY'))
    reg = owm.city_id_registry()
    lst = reg.ids_for(city_str, matching='like')
    print(lst)

def get_weather_info(loc=os.getenv('GEO_LOCATION')):

    owm = OWM(os.getenv('OWM_API_KEY'))

    coder = owm.geocoding_manager()
    loc_info = coder.geocode(loc)[0]
    
    mgr = owm.weather_manager()
    info = mgr.one_call(lon=loc_info.lon, lat=loc_info.lat, units='imperial', exclude=['minutely', 'hourly', 'alerts'])

    weather_dct = {'now': info.current.to_dict(),
                    'today': info.forecast_daily[0].to_dict()}

    for idx, forecast in enumerate(info.forecast_daily):
        if idx == 0:
            pass
        else:
            weather_dct[f'{idx} days from today'] = forecast.to_dict()

    print(weather_dct)

def simple_test(loc=os.getenv('GEO_LOCATION')):

    owm = OWM(os.getenv('OWM_API_KEY'))
    
    mgr = owm.weather_manager()
    info = mgr.one_call(lon=-73.6026271, lat=41.5620381)

def check_voices():

    voice = Voice.from_id('jTjySBclwibU6MA5gxG1')
    print(voice)
    # models_lst = Models.from_api()
    # print(models_lst)


if __name__ == '__main__':
    # check_loc('Pawling')
    # get_current_weather('Pawling,NY,US')
    # get_weather_info()
    # get_weather_info('Pawling,NY,US')
    # simple_test()
    check_voices()

