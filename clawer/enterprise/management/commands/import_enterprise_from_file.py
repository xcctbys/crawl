# coding=utf-8
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
from django.utils.encoding import smart_unicode

from html5helper.utils import wrapper_raven

from collector.utils_generator import CrawlerCronTab
from enterprise.models import Enterprise, Province
import time
import os
import traceback
import codecs

class Command(BaseCommand):

    help =" This command is used to import enterprises from file."

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('filename', nargs='?', help='enterprise filename')
        # Named (optional) arguments
        # parser.add_argument('--delete',
        #     action='store_true',
        #     dest='delete',
        #     default=False,
        #     help='Delete poll instead of closing it')
        pass


    # @wrapper_raven
    def handle(self, *args, **options):
        # print options
        filename = options['filename']
        if not os.path.exists(filename):
            print "The file %s doesn't exist!"%(filename)
            return
        start_time = time.time()
        print self.add(filename)
        # self.read(filename)
        end_time = time.time()
        print "Run time is %f s!"%(end_time - start_time)

    def add(self, filename):
        try:
            with codecs.open(filename, 'r+', 'gb2312') as f:
                success = 0
                failed = 0
                multiple = 0
                line_count = 0

                f.readline()
                for _line in lines[1:]:
                    print _line
                    line_count += 1
                    line = _line.strip().split(";")[0]
                    fields = line.strip().split(",")
                    if len(fields) < 3:
                        failed += 1
                        continue

                    name = smart_unicode(fields[0])
                    province = self.auto_fix_name(smart_unicode(fields[1]))
                    province_id = Province.to_id(province)
                    register_no = fields[2]


                    if not province_id:
                        failed += 1
                        continue
                    if not register_no:
                        register_no = "***"

                    if Enterprise.objects.filter(name=name).count() > 0:
                        multiple += 1
                        continue
                    # elif Enterprise.objects.filter(register_no=register_no).count() > 0:
                    #     multiple += 1
                    #     continue

                    Enterprise.objects.create(name=name, province=province_id, register_no=register_no)
                    success += 1

                return {"is_ok": True, "line_count": line_count, 'success': success, 'failed': failed, 'multiple': multiple}
        except Exception, e:
            print traceback.format_exc(10)
            print "Exception occured %s!"%(type(e))

    def auto_fix_name(self, province):
        if province==u"黑龙":
            return u"黑龙江"
        elif province ==u"内蒙":
            return u"内蒙古"
        return province


