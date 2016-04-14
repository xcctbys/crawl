#encoding=utf-8

import logging
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from collector.models import Job, CrawlerTask, CrawlerTaskGenerator, CrawlerGeneratorErrorLog

class DataPreprocess(object):

    def __init__(self, job_id):
        self.uris = None
        self.script = None
        self.schemes = ['http', 'https', 'ftp', 'ftps']
        job_doc = None
        try:
            job_doc = Job.objects.with_id(job_id)
        except Exception as e:
            logging.error("Can't find job_id: %s in mongodb!"%(job_id))
        self.job_id = job_id
        self.job = job_doc


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

    def __dereplicate_uris(self, uri_list):
        """ dereplicate uri list using APIs from other modules
            return dereplicated uri list
        """
        pass
        return uri_list

    def read_from_strings(self, textarea, schemes=None):
        """ validate strings from textarea with schemes
            return valid uri list
        """
        uri_list = textarea.strip().split()
        valid_uris = self.__validate_uris(uri_list, schemes)
        dereplicated_uris = self.__dereplicate_uris(valid_uris)
        self.uris = dereplicated_uris
        return dereplicated_uris

    def save_text(self, text, schemes=None):
        """
        """
        uris = self.read_from_strings(text, schemes)
        for uri in uris:
            try:
                CrawlerTask(job= self.job, uri= uri).save()
            except Exception as e:
                logging.error("error occured when saving uri-- %s"%(type(e)))
        return True

    def save_script(self, script, cron):
        """ saving script with cron settings to mongodb
            if params are None or saving excepts return False
            else return True
        """
        if script is None:
            logging.error("Error occured when saving script -- script is None")
            return False
        if cron is None:
            logging.error("Error occured when saving script -- cron is None")
            return False
        try:
            CrawlerTaskGenerator(job = self.job, code = script, cron = cron).save()
        except Exception as e:
            logging.error("Error occured when saving script --%s"%(type(e)))
            return False
        return True


    def save(self, text=None, script=None, settings=None):
        """ save uri(schemes) or script(cron) to mongodb server
            return True if success else False
        """
        if text is not None:
            try:
                schemes = settings['schemes'] if settings.has_key('schemes') else []
                assert self.save_text(text, schemes)
            except AssertionError :
                logging.error("Error occured when saving text")
        elif script is not None:
            if not settings.has_key('cron'):
                logging.error("cron is not found in settings")
                return
            try:
                assert self.save_script(script, settings['cron'])
            except AssertionError:
                logging.error("Error occured when saving script")
        else:
            logging.error("Please input text or script!")

