from sqlalchemy import MetaData, create_engine, Column, Integer, \
    ForeignKey, Float, String
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
# from tokenize import String
metadata = MetaData()
engine = create_engine('sqlite:///user_database', connect_args={'check_same_thread': False}, echo=False) # echo-False
Base = declarative_base()
db_session = sessionmaker(bind=engine)()


# Table city
# sqlalchemy is having  issues when handling similarly named columns explicitly naming added
class City(Base):
    __tablename__ = 'city'
    city_id = Column(Integer, primary_key=True)
    city_name = Column("city_name", String)
    city_climate = Column("city_climate", String)
    city_meteo_data = relationship("Meteo", backref="city")


# Table meteo
class Meteo(Base):
    __tablename__ = 'meteo'
    id = Column(Integer, primary_key=True)
    city_id = Column(ForeignKey('city.city_id'))
    month = Column(String)
    average_humidity = Column(Integer)
    average_temperature = Column(Float)


# Retrieving data from the database
# Retrieving data from the database
def get_cities():
    return db_session.query(City)


# Generating the set of average temperature values for a particular city
def get_city_temperature(city):
    return [month.average_temperature for month in city.city_meteo_data]


# Generating the set of average humidity values for a particular city
def get_city_humidity(city):
    return [month.average_humidity for month in city.city_meteo_data]


data = get_cities()
MONTHS = [record.month for record in data[0].city_meteo_data]
CITIES = [city.city_name for city in data]