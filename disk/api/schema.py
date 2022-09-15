"""
Модуль содержит схемы для валидации данных в запросах и ответах.
Схемы валидации запросов используются в бою для валидации данных, отправленных
клиентами.
Схемы валидации ответов *ResponseSchema используются только при тестировании,
чтобы убедиться, что обработчики возвращают данные в корректном формате.
"""
from datetime import date

from marshmallow import Schema, ValidationError, validates, validates_schema
from marshmallow.fields import Date, Dict, Float, Int, List, Nested, Str
from marshmallow.validate import Length, OneOf, Range

from disk.db.schema import ImportType


UPDATE_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class ImportSchema(Schema):
    id = Str(validate=Length(min=1), required=True)
    url = Str(validate=Length(min=1, max=256), required=False)
    parentId = Str(validate=Length(min=1), required=False)
    type = Str(validate=OneOf([type.value for type in ImportType]), required=True)
    size = Int(validate=Range(min=0), strict=True, required=False)


class NodeSchema(Schema):
    id = Str(validate=Length(min=1), required=True)
    url = Str(validate=Length(min=1, max=256), required=False)
    date = Date(format=UPDATE_DATE_FORMAT, required=True)
    parentId = Str(validate=Length(min=1), required=False)
    type = Str(validate=OneOf([type.value for type in ImportType]), required=True)
    size = Int(validate=Range(min=0), strict=True, required=False)
    children = Nested(lambda: NodeSchema(), many=True, required=False)


class ImportsSchema(Schema):
    items = Nested(ImportSchema(), many=True, required=True)
    updateDate = Date(format=UPDATE_DATE_FORMAT, required=True)


class DeleteIdSchema(Schema):
    id = Str(validate=Length(min=1), required=True)
    date = Date(format=UPDATE_DATE_FORMAT, required=True)


class NodeResponseSchema(Schema):
    data = Nested(NodeSchema(), required=True)


# class CitizensResponseSchema(Schema):
#     data = Nested(CitizenSchema(many=True), required=True)
#
#
# class PatchCitizenResponseSchema(Schema):
#     data = Nested(CitizenSchema(), required=True)
#
#
# class PresentsSchema(Schema):
#     citizen_id = Int(validate=Range(min=0), strict=True, required=True)
#     presents = Int(validate=Range(min=0), strict=True, required=True)


# Схема, содержащая кол-во подарков, которое купят жители по месяцам.
# Чтобы не указывать вручную 12 полей класс можно сгенерировать.
# CitizenPresentsByMonthSchema = type(
#     'CitizenPresentsByMonthSchema', (Schema,),
#     {
#         str(i): Nested(PresentsSchema(many=True), required=True)
#         for i in range(1, 13)
#     }
# )
#
#
# class CitizenPresentsResponseSchema(Schema):
#     data = Nested(CitizenPresentsByMonthSchema(), required=True)
#
#
# class TownAgeStatSchema(Schema):
#     town = Str(validate=Length(min=1, max=256), required=True)
#     p50 = Float(validate=Range(min=0), required=True)
#     p75 = Float(validate=Range(min=0), required=True)
#     p99 = Float(validate=Range(min=0), required=True)
#
#
# class TownAgeStatResponseSchema(Schema):
#     data = Nested(TownAgeStatSchema(many=True), required=True)


class ErrorSchema(Schema):
    code = Str(required=True)
    message = Str(required=True)


class ErrorResponseSchema(Schema):
    error = Nested(ErrorSchema(), required=True)
