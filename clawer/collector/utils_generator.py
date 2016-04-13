#encoding=utf-8

import logging
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from collector.models import Job, CrawlerTask, CrawlerTaskGenerator, CrawlerGeneratorErrorLog, CrawlerGeneratorAlertLog, GrawlerGeneratorCronLog

class DataPreprocess(object):

    def __init__(self, job_id):
        self.uris = None
        self.script = None
        self.job_id = job_id
        self.schemes = ['http', 'https', 'ftp', 'ftps']
        pass

    def __validate_uris(self, uri_list, schemes=None):
        """ validate uri from uri list,
            return valid uri list
        """
        uris=[]
        if not isinstance(uri_list, list):
            return uris
        # you can add param by yourself, default: schemes=['http', 'https', 'ftp', 'ftps']
        if schemes is not None and isinstance(schemes, list):
            self.schemes.extend(schemes)
        val = URLValidator(self.schemes)
        for uri in uri_list:
            try:
                val(uri)
                uris.append(uri)
            except ValidationError, e:
                logging.error("URI ValidationError: %s" %(uri))

        return uris

    def read_from_strings(self, textarea, schemes=None):
        """ validate strings from textarea with schemes
            return valid uri list
        """
        uri_list = textarea.strip().split()
        valid_uris = self.__validate_uris(uri_list, schemes)
        dereplicated_uris = self.__dereplicate_uris(valid_uris)
        self.uris = dereplicated_uris
        return dereplicated_uris



    def __dereplicate_uris(self, uri_list):
        """ dereplicate uri list using APIs from other modules
            return dereplicated uri list
        """
        pass
        return uri_list

    def save_uris(self, uris):
        """
        """
        job_doc = Job.objects(id = self.job_id).first()
        if job_doc is None:
            logging.error("Can't find job_id: %s in mongodb!"%(self.job_id))
            return False

        for uri in uris:
            try:
                CrawlerTask(job= job_doc, uri= uri).save()
            except Exception as e:
                logging.error("error occured when saving uri-- %s"%(type(e)))
        return True

    def save(self):
        """ save uri or script to mongodb server
            return True if success else False
        """
        if self.uris is not None:
            self.save_uris(uris)
        elif self.script is not None:
            pass

        return True

    def data_preprocess(*args, **kwargs):
        return True



