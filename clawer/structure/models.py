# -*- coding: utf-8 -*-

from storage.models import Job
from mongoengine import (Document,
                         IntField,
                         StringField,
                         ReferenceField,)


class Parser(Document):
    parser_id = IntField()
    python_script = StringField()


class StructureConfig(Document):
    job = ReferenceField(Job)
    parser = ReferenceField(Parser)
    db_xml = StringField()
