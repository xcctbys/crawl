# -*- coding: utf-8 -*-

from storage import Job
from mongoengine import (Document,
                         IntField,
                         TextField,
                         ReferenceField,)


class Parser(Document):
    parser_id = IntField()
    python_script = TextField()


class StructureConfig(Document):
    job = ReferenceField(Job)
    parser = ReferenceField(Parser)
    db_xml = TextField()
