from repository.repo import Repository
from repository.mappers.tta150_parametro import Tta150Parametro

a = Repository().get(mapper=Tta150Parametro)
print(a)