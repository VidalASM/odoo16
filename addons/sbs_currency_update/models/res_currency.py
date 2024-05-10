from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
import pytz
import logging
import urllib.request
import urllib.parse
import ssl

_logger = logging.getLogger(__name__)


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _action_sbs_currency_update(self, date):
        url = 'http://www.sbs.gob.pe/app/pp/SISTIP_PORTAL/Paginas/Publicacion/TipoCambioPromedio.aspx'
        try:
            context = ssl._create_unverified_context()
            open_html = urllib.request.urlopen(url,context=context)
            html = BeautifulSoup(open_html, "lxml")
            tr_dollar = html.find("tr", id="ctl00_cphContent_rgTipoCambio_ctl00__0")
            currency = self.env.ref('base.USD')
            peru_id = self.env.ref('base.pe')
            if tr_dollar and currency and peru_id == self.env.company.country_id:
                tds_dollar = tr_dollar.findAll("td", {"class": "APLI_fila2"})
                if tds_dollar:
                    values = {
                        'compra': float(tds_dollar[0].text.strip()),
                        'venta': float(tds_dollar[1].text.strip()),
                    }
                    rate_date = fields.Datetime.now().replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(self.env.user.tz or 'UTC')) + relativedelta(days=1)
                    if date:
                        rate_date = datetime.strptime(date, "%Y-%m-%d") + relativedelta(days=1)
                    currency_rate = self.env['res.currency.rate']
                    for company_id in (1,2):
                        rate = currency_rate.search([
                            ('currency_id', '=', currency.id),
                            ('name', '=', rate_date.date()),
                            ('company_id', '=', company_id)
                        ], limit=1)

                        if not rate:
                            currency_rate.create({
                                'currency_id': currency.id,
                                'rate': 1.0 / values['venta'],
                                'name': rate_date,
                                'company_id': company_id,
                            })
                        else:
                            rate.write({
                                'rate': 1.0 / values['venta'],
                                'name': rate_date,
                                'company_id': company_id,
                            })
        except urllib.error.HTTPError as http_error:
            _logger.warning('Error: {}'.format(http_error))
        except urllib.error.URLError as url_error:
            _logger.warning('Error: {}'.format(url_error))
        except Exception as exception_error:
            _logger.warning('Error: {}'.format(exception_error))
