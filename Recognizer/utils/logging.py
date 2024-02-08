# -*- coding: utf-8 -*-
import logging
import datetime

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    #level=logging.INFO,
                    # filename=f'Services-from-{datetime.datetime.now().date()}.log',
                    filemode='a',
                    level=logging.DEBUG,  # Можно заменить на другой уровень логирования.
                    )
