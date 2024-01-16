import requests
from odoo import fields, api, models, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    state = fields.Selection([('ACTIVO', 'ACTIVO'),
                            ('BAJA DE OFICIO', 'BAJA DE OFICIO'),
                            ('BAJA DEFINITIVA', 'BAJA DEFINITIVA'),
                            ('BAJA PROVISIONAL', 'BAJA PROVISIONAL'),
                            ('SUSPENSION TEMPORAL', 'BAJA PROVISIONAL'),
                            ('INHABILITADO-VENT.UN', 'INHABILITADO-VENT.UN'),
                            ('BAJA MULT.INSCR. Y O', 'BAJA MULT.INSCR. Y O'),
                            ('PENDIENTE DE INI. DE', 'PENDIENTE DE INI. DE'),
                            ('OTROS OBLIGADOS', 'OTROS OBLIGADOS'),
                            ('NUM. INTERNO IDENTIF', 'NUM. INTERNO IDENTIF'),
                            ('ANUL.PROVI.-ACTO ILI', 'ANUL.PROVI.-ACTO ILI'),
                            ('ANULACION - ACTO ILI', 'ANULACION - ACTO ILI'),
                            ('BAJA PROV. POR OFICIO', 'BAJA PROV. POR OFICIO'),
                            ('ANULACION - ERROR SU', 'ANULACION - ERROR SU')], "Partner State", default="ACTIVO")
    condition = fields.Selection([('HABIDO', 'HABIDO'),
                                ('NO HABIDO', 'NO HABIDO'),
                                ('', 'NO HABIDO'),
                                ('NO HALLADO', 'NO HALLADO'),
                                ('PENDIENTE', 'PENDIENTE'),
                                ('NO HALLADO SE MUDO D', 'NO HALLADO SE MUDO D'),
                                ('NO HALLADO NO EXISTE', 'NO HALLADO NO EXISTE'),
                                ('NO HALLADO FALLECIO', 'NO HALLADO FALLECIO'),
                                ('-', 'NO HABIDO'),
                                ('NO HALLADO OTROS MOT','NO HALLADO OTROS MOT'),
                                ('NO APLICABLE', 'NO APLICABLE'),
                                ('NO HALLADO NRO.PUERT', 'NO HALLADO NRO.PUERT'),
                                ('NO HALLADO CERRADO', 'NO HALLADO CERRADO'),
                                ('POR VERIFICAR', 'POR VERIFICAR'),
                                ('NO HALLADO DESTINATA', 'NO HALLADO DESTINATA'),
                                ('NO HALLADO RECHAZADO', 'NO HALLADO RECHAZADO')], 'Condition')

    def update_document(self):
        self._doc_number_change()

    # Función heredada del modulo base_address_city para colocar el zip correcto
    def _onchange_city_id(self):
        res = super(ResPartner, self)._onchange_city_id()
        self.zip = self.l10n_pe_district.code
        return res

    @api.onchange('company_type')
    def _onchange_company_type(self):
        if not self.vat:
            if self.company_type == 'person':
                self.l10n_latam_identification_type_id = self.env['l10n_latam.identification.type'].search([('name','=','DNI')], limit=1)
            else:
                self.l10n_latam_identification_type_id = self.env['l10n_latam.identification.type'].search([('name','=','RUC')], limit=1)

    @api.onchange('vat','l10n_latam_identification_type_id')
    def _doc_number_change(self):
        vat = self.vat
        vat_type = self.l10n_latam_identification_type_id.l10n_pe_vat_code
        if vat and vat_type:
            if vat_type == '1':
                if len(vat) != 8:
                    raise UserError(_('The DNI entered is incorrect'))
                self.ConsultarDNI(vat)
            elif vat_type=="6":
                self.ValidarRUC(vat)
                self.ConsultarRUC(vat)

    def ConsultarDNI(self, numeroDNI):
        # consultamos el dni
        try:
            # realizamos la consulta a la api
            result = requests.get(f'https://api.apis.net.pe/v1/dni?numero={numeroDNI}')
            # convertimos el resultado a un diccionario
            if result.status_code == 404:
                raise UserError(_('DNI not found.'))
            jsonedResponse = result.json()
            self.name = jsonedResponse['nombres'] + ' ' + jsonedResponse['apellidoPaterno'] + ' ' +  jsonedResponse['apellidoMaterno']
        except Exception as e:
            raise UserError(e)
    
    @api.model
    def l10n_pe_dni_connection(self, numeroDNI):
        data = {}
        try:
            result = requests.get(f'https://api.apis.net.pe/v1/dni?numero={numeroDNI}')
            if result.status_code == 404:
                raise UserError(_('DNI not found.'))
            jsonedResponse = result.json()
            name = jsonedResponse['nombres'] + ' ' + jsonedResponse['apellidoPaterno'] + ' ' +  jsonedResponse['apellidoMaterno']
            data['nombre'] = name
        except Exception :
            data = False 
        return data  
    
    @api.model     
    def l10n_pe_ruc_connection(self, ruc):
        data = {}
        urlReferencia = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
        sesion = requests.Session()
        payload={}
        headers = {
        'Host': 'e-consultaruc.sunat.gob.pe',
        'Origin': 'https://e-consultaruc.sunat.gob.pe',
        'Referer': urlReferencia,
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }

        numeroDNI = "12345678";
        url = f"https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorTipdoc&razSoc=&nroRuc=&nrodoc={numeroDNI}&contexto=ti-it&modo=1&search1=&rbtnTipo=2&tipdoc=1&search2={numeroDNI}&search3=&codigo="
        contenidoHTML = ""
        nIntentos = 0
        codigoEstado = 401
        consRuc = False
        consRepLeg = False
        consLocAnex = False
        while(nIntentos < 15 and codigoEstado == 401):
            response = sesion.request("POST", url, headers=headers, data=payload, verify=True)
            codigoEstado = response.status_code
            contenidoHTML = response.text 
            nIntentos = nIntentos + 1
        if not consRuc or not consRepLeg or not consLocAnex:
            numeroRandom = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, "name=\"numRnd\" value=\"", "\">")

        url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorRuc&nroRuc=%s&contexto=ti-it&modo=1&numRnd=%s" % (ruc, numeroRandom)
        response = sesion.request("POST", url, headers=headers, data=payload, verify=True)
        contenidoHTML = response.text

        if(response.status_code == 200):
            oEnSUNAT = self.ObtenerDatosRUC(contenidoHTML)
            if (oEnSUNAT.TipoRespuesta == 1):
                splited = oEnSUNAT.RUC.split('-')
                name = splited[1]
                # Si el nombre lleva un guión agreamos el resto
                if len(splited)>1:
                    for i in range(2, len(splited)):
                        name += '-' + splited[i]
                data['ruc'] = name
                data['business_name'] = name

                country_id = self.env['res.country'].search([('code','=','PE')])
                parts = oEnSUNAT.DomicilioFiscal.split('-')
                city = parts[-2].strip().title()
                state = parts[-3].strip().title()
                if city == 'Prov. Const. Del Callao':
                    city = 'Callao'
                    state = 'Callao'
                if '(' in oEnSUNAT.DomicilioFiscal:
                    street = oEnSUNAT.DomicilioFiscal.split('(')[0].strip()
                else:
                    street = oEnSUNAT.DomicilioFiscal.split('-')[0]
                    street = " ".join(street.split())
                    street = street.rsplit(' ', 1)[0]
                for i in range(1, len(state)):
                    state_id = self.env['res.country.state'].search([('name','like',state),('country_id','=',country_id.id)], limit=1) if state else False
                    if state_id:
                        break
                    else:
                        state = state[1:]
                state_id = self.env['res.country.state'].search([('name','ilike',state),('country_id','=',country_id.id)]) if state else False
                data['residence'] = street
                data['country_id'] = country_id.id
                data['state_id'] = state_id.id if state_id else False
        else:
            data = False 
        return data  

    def ValidarRUC(self, numeroRUC):
        tipoRespuesta = 2
        mensajeRespuesta = ""
        nValor = len(numeroRUC)
        if(nValor == 11):
            if numeroRUC.isdigit():
                tipoRespuesta = 1
            else:
                mensajeRespuesta = _("The RUC number '%s' should only have numeric characters.") % (numeroRUC)
        else:
            mensajeRespuesta = _("The RUC number '%s' have %d %s and it should be 11 characters.") % (numeroRUC, nValor, "character" if nValor==1 else "characters")
        if(tipoRespuesta > 1):
            raise UserError(mensajeRespuesta) 
        return tipoRespuesta, mensajeRespuesta

    def ObtenerDatosRUC(self, contenidoHTML):
        oEnSUNAT = EnSUNAT()
        nombreInicio = ""
        nombreFin = ""
        posicion = 0
        arrResultado = list()

        nombreInicio = "<HEAD><TITLE>"
        nombreFin = "</TITLE></HEAD>"
        contenidoBusqueda = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
        if (contenidoBusqueda == ".:: Pagina de Mensajes ::."):
            nombreInicio = "<p class=\"error\">"
            nombreFin = "</p>"
            oEnSUNAT.TipoRespuesta = 2
            oEnSUNAT.MensajeRespuesta = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
        elif (contenidoBusqueda == ".:: Pagina de Error ::."):
            nombreInicio = "<p class=\"error\">"
            nombreFin = "</p>"
            oEnSUNAT.TipoRespuesta = 3
            oEnSUNAT.MensajeRespuesta = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
        else:
            oEnSUNAT.TipoRespuesta = 2

            nombreInicio = "<div class=\"list-group\">"
            nombreFin = "<div class=\"panel-footer text-center\">"
            contenidoBusqueda = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
            if (contenidoBusqueda == ""):
                nombreInicio = "<strong>"
                nombreFin = "</strong>"
                oEnSUNAT.MensajeRespuesta = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
                if(oEnSUNAT.MensajeRespuesta == ""):
                    oEnSUNAT.MensajeRespuesta = "No se puede obtener los datos del RUC, porque no existe la clase principal \"list-group\" en el contenido HTML"
            else:
                nombreInicio = "<h4 class=\"list-group-item-heading\">"
                nombreFin = "</h4>"
                posicion = 0

                arrResultado = self.ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                if(len(arrResultado)> 0):
                    posicion = int(arrResultado[0])
                    arrResultado = self.ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                    posicion = int(arrResultado[0])
                    oEnSUNAT.RUC = arrResultado[1]
                    oEnSUNAT.TipoRespuesta = 1
                else:
                    oEnSUNAT.MensajeRespuesta = "No se puede obtener la \"Razon Social\", porque no existe la clase \"list-group-item-heading\" en el contenido HTML"

                if(oEnSUNAT.TipoRespuesta == 1):
                    '''
                    # Mensaje cuando el estado es "BAJA DE OFICIO" caso contrario inicia con "Tipo Contribuyente"
                    # Tipo Contribuyente
                    # Nombre Comercial
                    # Fecha de Inscripción
                    # Fecha de Inicio de Actividades
                    # Estado del Contribuyente
                    # Condición del Contribuyente
                    # Domicilio Fiscal
                    # Sistema Emisión de Comprobante
                    # Actividad Comercio Exterior
                    # Sistema Contabilidiad
                    # Emisor electrónico desde:
                    # Comprobantes Electrónicos:
                    # Afiliado al PLE desde
                    # n/a
                    '''
                    lCadena = list()
                    nombreInicio = "<p class=\"list-group-item-text\">"
                    nombreFin = "</p>"
                    posicion = 0
                    arrResultado = self.ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                    while(len(arrResultado)>0):
                        posicion = int(arrResultado[0])
                        lCadena.append(arrResultado[1].strip())
                        arrResultado = self.ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                    if(len(lCadena) == 0):
                        oEnSUNAT.TipoRespuesta = 2
                        oEnSUNAT.MensajeRespuesta = "No se puede obtener los datos básicos, porque no existe la clase \"list-group-item-text\" en el contenido HTML"
                    else:
                        inicio = 0 
                        if(len(lCadena) > 14): # Si estado es "BAJA DE OFICIO" caso contrario es 14
                            inicio = 1
                        oEnSUNAT.TipoContribuyente = lCadena[inicio]
                        oEnSUNAT.NombreComercial = lCadena[inicio + 1]
                        oEnSUNAT.FechaInscripcion = lCadena[inicio + 2]
                        oEnSUNAT.FechaInicioActividades = lCadena[inicio + 3]
                        oEnSUNAT.EstadoContribuyente = lCadena[inicio + 4]
                        oEnSUNAT.CondicionContribuyente = lCadena[inicio + 5]
                        oEnSUNAT.DomicilioFiscal = lCadena[inicio + 6]
                        oEnSUNAT.SistemaEmisionComprobante = lCadena[inicio + 7]
                        oEnSUNAT.ActividadComercioExterior = lCadena[inicio + 8]
                        oEnSUNAT.SistemaContabilidiad = lCadena[inicio + 9]
                        oEnSUNAT.EmisorElectrónicoDesde = lCadena[inicio + 10]
                        oEnSUNAT.ComprobantesElectronicos = lCadena[inicio + 11]
                        oEnSUNAT.AfiliadoPLEDesde = lCadena[inicio + 12]

                        '''
                        # Actividad(es) Económica(s)
                        # Comprobantes de Pago c/aut. de impresión (F. 806 u 816)
                        # Sistema de Emisión Electrónica # (opcional, em algunos casos no aparece)
                        # Padrones 
                        '''
                        lCadena = list()
                        nombreInicio = "<tbody>"
                        nombreFin = "</tbody>"
                        posicion = 0
                        arrResultado = self.ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                        while(len(arrResultado)>0):
                            posicion = int(arrResultado[0])
                            lCadena.append(arrResultado[1].strip().replace('\r\n', ' ').replace('\t', ' '))
                            arrResultado = self.ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                        if(len(lCadena) == 0):
                            oEnSUNAT.TipoRespuesta = 2
                            oEnSUNAT.MensajeRespuesta = "No se puede obtener los datos de las tablas, porque no existe el tag \"tbody\" en el contenido HTML"
                        else:
                            oEnSUNAT.ActividadesEconomicas = lCadena[0]
                            oEnSUNAT.ComprobantesPago = lCadena[1]
                            if(len(lCadena) == 4):
                                oEnSUNAT.SistemaEmisionElectrónica = lCadena[2]
                                oEnSUNAT.Padrones = lCadena[3]
                            else:
                                oEnSUNAT.Padrones = lCadena[2]

        return oEnSUNAT

    def ObtenerDatosRepresentantesLegales(self, contenidoHTML):
        oEnSUNAT = EnSUNAT()
        nombreInicio = ""
        nombreFin = ""
        posicion = 0
        arrResultado = list()

        nombreInicio = "<HEAD><TITLE>"
        nombreFin = "</TITLE></HEAD>"
        contenidoBusqueda = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
        if (contenidoBusqueda == ".:: Pagina de Mensajes ::."):
            nombreInicio = "<p class=\"error\">"
            nombreFin = "</p>"
            oEnSUNAT.TipoRespuesta = 2
            oEnSUNAT.MensajeRespuesta = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
        elif (contenidoBusqueda == ".:: Pagina de Error ::."):
            nombreInicio = "<p class=\"error\">"
            nombreFin = "</p>"
            oEnSUNAT.TipoRespuesta = 3
            oEnSUNAT.MensajeRespuesta = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
        else:
            oEnSUNAT.TipoRespuesta = 2
            nombreInicio = "<td align=\""
            nombreFin = "</td>"
            posicion = 0
            rep = {}
            contador = 0
            while True:
                arrResultado = self.ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                contenidoBusqueda = self.ExtraerContenidoEntreTagString(contenidoHTML, posicion, nombreInicio, nombreFin)
                if(len(arrResultado)> 0):
                    posicion = int(arrResultado[0])
                    rep[contador] = contenidoBusqueda[contenidoBusqueda.find('>')+1:].strip()
                    contador += 1
                    if contador % 5 == 0:
                        oEnSUNAT.RepresentantesLesgales.append(rep)
                        contador = 0
                        rep = {}
                if contenidoBusqueda == "":
                    break
                else:
                    oEnSUNAT.TipoRespuesta = 1
        return oEnSUNAT
        
    def ObtenerDatosLocalesAnexos(self, contenidoHTML):
        oEnSUNAT = EnSUNAT()
        nombreInicio = ""
        nombreFin = ""
        posicion = 0
        arrResultado = list()

        nombreInicio = "<HEAD><TITLE>"
        nombreFin = "</TITLE></HEAD>"
        contenidoBusqueda = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
        if (contenidoBusqueda == ".:: Pagina de Mensajes ::."):
            nombreInicio = "<p class=\"error\">"
            nombreFin = "</p>"
            oEnSUNAT.TipoRespuesta = 2
            oEnSUNAT.MensajeRespuesta = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
        elif (contenidoBusqueda == ".:: Pagina de Error ::."):
            nombreInicio = "<p class=\"error\">"
            nombreFin = "</p>"
            oEnSUNAT.TipoRespuesta = 3
            oEnSUNAT.MensajeRespuesta = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
            if oEnSUNAT.MensajeRespuesta == 'No se encontró información para locales anexos.':
                oEnSUNAT.TipoRespuesta = 1
        else:
            oEnSUNAT.TipoRespuesta = 2
            nombreInicio = "<table class=\"table\">"
            nombreFin = "</table>"
            posicion = 0
            contenidoHTML = self.ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)[1]
            nombreInicio = "<td align=\""
            nombreFin = "</td>"
            posicion = 0
            local = {}
            contador = 0
            while True:
                arrResultado = self.ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                contenidoBusqueda = self.ExtraerContenidoEntreTagString(contenidoHTML, posicion, nombreInicio, nombreFin)
                if(len(arrResultado)> 0):
                    posicion = int(arrResultado[0])
                    local[contador] = contenidoBusqueda[contenidoBusqueda.find('>')+1:].strip()
                    contador += 1
                    if contador % 4 == 0:
                        oEnSUNAT.LoacalesAnexos.append(local)
                        contador = 0
                        local = {}
                if contenidoBusqueda == "":
                    break
                else:
                    oEnSUNAT.TipoRespuesta = 1
        return oEnSUNAT

    def ConsultarRepresentantesLegales(self, sesion, urlReferencia, desRuc, numeroRUC, numeroRandom):
        tipoRespuesta = 2
        mensajeRespuesta = ""

        payload={}
        headers = {
        'Host': 'e-consultaruc.sunat.gob.pe',
        'Origin': 'https://e-consultaruc.sunat.gob.pe',
        'Referer': urlReferencia,
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }
        url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=getRepLeg&desRuc=%s&nroRuc=%s&contexto=ti-it&modo=1&numRnd=%s" % (desRuc, numeroRUC, numeroRandom)
        response = sesion.request("POST", url, headers=headers, data=payload, verify=True)
        contenidoHTML = response.text
        

        if(response.status_code == 200):
            oEnSUNAT = self.ObtenerDatosRepresentantesLegales(contenidoHTML)
            if (oEnSUNAT.TipoRespuesta == 1):
                if not self._origin:
                    self.child_ids = False
                if oEnSUNAT.RepresentantesLesgales and self.is_company:
                    for rep in oEnSUNAT.RepresentantesLesgales:
                        if rep[3] in ["GERENTE GENERAL", "TITULAR-GERENTE", "GERENTE", "APODERADO"]:
                           contact={}
                           contact['name']= rep[2].replace('  ',' ').replace('  ','').strip()
                           if self.search_count([('name', '=', contact['name']), ('parent_id', '=', self.id)]) == 0:
                               contact['function']=rep[3]
                               contact['type']='contact'
                               contact['parent_id']=self.id
                               contact['display_name']=self.name + ', ' + contact['name']
                               contact['is_company']=False
                               contact['commercial_partner_id']=self.id
                               contact['commercial_company_name']=self.name
                               self.child_ids=[(0, None, contact)]
                tipoRespuesta = 1
            else:
                tipoRespuesta = oEnSUNAT.TipoRespuesta
                mensajeRespuesta = _("Could not get data for RUC %s.\r\nDetails: %s") % (numeroRUC, oEnSUNAT.MensajeRespuesta)
                raise UserError(mensajeRespuesta)
        # else:
        #     self.ConsultarRUC(numeroRUC)
        
        return tipoRespuesta, mensajeRespuesta, response.status_code

    def ConsultarContenidoRUC(self, sesion, urlReferencia, numeroRUC, numeroRandom):
        tipoRespuesta = 2
        mensajeRespuesta = ""

        payload={}
        headers = {
        'Host': 'e-consultaruc.sunat.gob.pe',
        'Origin': 'https://e-consultaruc.sunat.gob.pe',
        'Referer': urlReferencia,
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }
        url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorRuc&nroRuc=%s&contexto=ti-it&modo=1&numRnd=%s" % (numeroRUC, numeroRandom)
        response = sesion.request("POST", url, headers=headers, data=payload, verify=True)
        contenidoHTML = response.text
        

        if(response.status_code == 200):
            oEnSUNAT = self.ObtenerDatosRUC(contenidoHTML)
            if (oEnSUNAT.TipoRespuesta == 1):
                splited = oEnSUNAT.RUC.split('-')
                name = splited[1]
                # Si el nombre lleva un guión agreamos el resto
                if len(splited)>1:
                    for i in range(2, len(splited)):
                        name += '-' + splited[i]
                self.name = name
                country_id = self.env['res.country'].search([('code','=','PE')])
                parts = oEnSUNAT.DomicilioFiscal.split('-')
                district = parts[-1].strip().title()
                city = parts[-2].strip().title()
                state = parts[-3].strip().title()
                # Solo para el callao
                if city == 'Prov. Const. Del Callao':
                    district = 'Callao'
                    city = 'Callao'
                    state = 'Callao'
                else:
                    state = parts[-3].strip().title()
                # district = parts[len(parts)-1].strip()
                # city = parts[len(parts)-2].strip()
                # state = parts[len(parts)-3].split()[-1] if len(parts) >= 3 else ''
                if '(' in oEnSUNAT.DomicilioFiscal:
                    street = oEnSUNAT.DomicilioFiscal.split('(')[0].strip()
                else:
                    street = oEnSUNAT.DomicilioFiscal.split('-')[0]
                    street = " ".join(street.split())
                    street = street.rsplit(' ', 1)[0]
                for i in range(1, len(state)):
                    state_id = self.env['res.country.state'].search([('name','like',state),('country_id','=',country_id.id)], limit=1) if state else False
                    if state_id:
                        break
                    else:
                        state = state[1:]
                state_id = self.env['res.country.state'].search([('name','ilike',state),('country_id','=',country_id.id)]) if state else False
                city_id  = self.env['res.city'].search([('name','ilike',city),('country_id','=',country_id.id)]) if city else False
                district_id = self.env['l10n_pe.res.city.district'].search([('name','ilike',district),('city_id','=',city_id.id)]) if district else False
                if district_id and len(district_id)>1:
                    for dis in district_id:
                        if dis.name.upper() == district.upper():
                            final_district = dis
                else:
                    final_district = district_id

                self.country_id = country_id
                self.l10n_pe_district = final_district
                self.city_id = city_id
                self.state_id = state_id
                self.street = street
                self.zip = final_district.code if final_district else ''
                self.state = oEnSUNAT.EstadoContribuyente
                self.condition = oEnSUNAT.CondicionContribuyente

                tipoRespuesta = 1
            else:
                tipoRespuesta = oEnSUNAT.TipoRespuesta
                mensajeRespuesta = _("Could not get data for RUC %s.\r\nDetails: %s") % (numeroRUC, oEnSUNAT.MensajeRespuesta)
                raise UserError(mensajeRespuesta)
        # else:
        #     self.ConsultarRUC(numeroRUC)
        
        return tipoRespuesta, mensajeRespuesta, response.status_code

    def ConsultarLocalesAnexos(self, sesion, urlReferencia, desRuc, numeroRUC, numeroRandom):
        tipoRespuesta = 2
        mensajeRespuesta = ""

        payload={}
        headers = {
        'Host': 'e-consultaruc.sunat.gob.pe',
        'Origin': 'https://e-consultaruc.sunat.gob.pe',
        'Referer': urlReferencia,
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }
        url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=getLocAnex&desRuc=%s&nroRuc=%s&contexto=ti-it&modo=1&numRnd=%s" % (desRuc, numeroRUC, numeroRandom)
        response = sesion.request("POST", url, headers=headers, data=payload, verify=True)
        contenidoHTML = response.text
        

        if(response.status_code == 200):
            oEnSUNAT = self.ObtenerDatosLocalesAnexos(contenidoHTML)
            if oEnSUNAT.TipoRespuesta == 1:

                
                if oEnSUNAT.LoacalesAnexos and self.is_company:
                    for local in oEnSUNAT.LoacalesAnexos:
                        contact={}
                        contact['name']= local[0] + ' - ' + local[1]
                        district = local[2].split('-')[-1].strip().title()
                        city = local[2].split('-')[-2].strip().title()
                        state = local[2].split('-')[-3].strip().title()
                        # Solo para el callao
                        if city == 'Prov. Const. Del Callao':
                            district = 'Callao'
                            city = 'Callao'
                            state = 'Callao'
                        else:
                            state = local[-3].strip().title()
                        country_id = self.env['res.country'].search([('code','=','PE')])
                        for i in range(1, len(state)):
                            state_id = self.env['res.country.state'].search([('name','like',state),('country_id','=',country_id.id)], limit=1) if state else False
                            if state_id:
                                break
                            else:
                                state = state[1:]
                        city_id  = self.env['res.city'].search([('name','ilike',city),('state_id', '=', state_id.id),('country_id','=',country_id.id)], limit=1) if city else False
                        district_id = self.env['l10n_pe.res.city.district'].search([('name','ilike',district),('city_id','=',city_id.id)], limit=1) if district else False
                        if self.search_count([('name', '=', contact['name']), ('parent_id', '=', self.id)]) == 0:
                            contact['street'] = local[2].replace('  ', ' ').replace('  ', '').strip()
                            contact['l10n_pe_district'] = district_id
                            contact['city_id'] = city_id
                            contact['state_id'] = state_id
                            contact['country_id'] = country_id
                            contact['zip'] = district_id.code
                            contact['type'] = 'delivery'
                            contact['parent_id'] = self.id
                            contact['display_name'] = self.name + ', ' + contact['name']
                            contact['is_company'] = False
                            contact['commercial_partner_id'] = self.id
                            contact['commercial_company_name'] = self.name
                            self.child_ids = [(0, None, contact)]
                tipoRespuesta = 1
            else:
                tipoRespuesta = oEnSUNAT.TipoRespuesta
                mensajeRespuesta = _("Could not get data for RUC %s.\r\nDetails: %s") % (numeroRUC, oEnSUNAT.MensajeRespuesta)
                raise UserError(mensajeRespuesta)
        # else:
        #     self.ConsultarRUC(numeroRUC)
        
        return tipoRespuesta, mensajeRespuesta, response.status_code

    def ConsultarRUC(self, numeroRUC):
        # tipoRespuesta = 2
        mensajeRespuesta = ""

        try:
            urlInicial = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
            payload={}
            headers = {
              'Host': 'e-consultaruc.sunat.gob.pe',
              'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
              'sec-ch-ua-mobile': '?0',
              'Sec-Fetch-Dest': 'document',
              'Sec-Fetch-Mode': 'navigate',
              'Sec-Fetch-Site': 'none',
              'Sec-Fetch-User': '?1',
              'Upgrade-Insecure-Requests': '1',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
            }

            sesion = requests.Session()
            response = sesion.request("GET", urlInicial, headers=headers, data=payload, verify=True)

            if(response.status_code == 200):
                payload={}
                headers = {
                'Host': 'e-consultaruc.sunat.gob.pe',
                'Origin': 'https://e-consultaruc.sunat.gob.pe',
                'Referer': urlInicial,
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
                'sec-ch-ua-mobile': '?0',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
                }

                numeroDNI = "12345678"; # cualquier número DNI pero que exista en SUNAT.
                url = f"https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorTipdoc&razSoc=&nroRuc=&nrodoc={numeroDNI}&contexto=ti-it&modo=1&search1=&rbtnTipo=2&tipdoc=1&search2={numeroDNI}&search3=&codigo="
                
                contenidoHTML = ""
                nIntentos = 0
                codigoEstado = 401
                consRuc = False
                consRepLeg = False
                consLocAnex = False
                # Validamos que intente hasta 15 veces si el código de respuesta es 401 Unauthorized
                while(nIntentos < 15 and codigoEstado == 401):
                    response = sesion.request("POST", url, headers=headers, data=payload, verify=True)
                    codigoEstado = response.status_code
                    contenidoHTML = response.text 
                    nIntentos = nIntentos + 1

                if not consRuc or not consRepLeg or not consLocAnex:
                    numeroRandom = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, "name=\"numRnd\" value=\"", "\">")
                    # Validamos que intente hasta 15 veces si el código de respuesta es 401 Unauthorized
                    nIntentos = 0
                    codigoEstado = 401
                    while(nIntentos < 15 and not consRuc):
                        tipoRespuesta, mensajeRespuesta, codigoEstado = self.ConsultarContenidoRUC(sesion, urlInicial, numeroRUC, numeroRandom)
                        nIntentos = nIntentos + 1
                        if codigoEstado == 200:
                            consRuc = True
                    # Validamos que intente hasta 15 veces si el código de respuesta es 401 Unauthorized
                    if self.env.company.legal_representatives:
                        nIntentos = 0
                        codigoEstado = 401
                        while(nIntentos < 15 and not consRepLeg):
                            tipoRespuesta, mensajeRespuesta, codigoEstado = self.ConsultarRepresentantesLegales(sesion, urlInicial, self.name, numeroRUC, numeroRandom)
                            nIntentos = nIntentos + 1
                            if codigoEstado == 200:
                                consRepLeg = True
                    # Validamos que intente hasta 15 veces si el código de respuesta es 401 Unauthorized
                    if self.env.company.annexed_locals:
                        nIntentos = 0
                        codigoEstado = 401
                        while(nIntentos < 15 and not consLocAnex):
                            tipoRespuesta, mensajeRespuesta, codigoEstado = self.ConsultarLocalesAnexos(sesion, urlInicial, self.name, numeroRUC, numeroRandom)
                            nIntentos = nIntentos + 1
                            if codigoEstado == 200:
                                consLocAnex = True
                else:
                    mensajeRespuesta = "Ocurrió un inconveniente1 (%s) al consultar el número ramdom del RUC %s.\r\nDetalle: %s" % (response.status_code, numeroRUC, contenidoHTML)                
                    raise UserError(mensajeRespuesta)
            else:
                self.ConsultarRUC(numeroRUC)
        except Exception as e:
            raise UserError(e)

    def ExtraerContenidoEntreTagString(self, cadena, posicion, nombreInicio, nombreFin, sensitivo=False):
        respuesta = ""
        if(sensitivo):
            cadena2 = cadena.lower()
            nombreInicio = nombreInicio.lower()
            nombreFin=nombreFin.lower()
            posicionInicio = cadena2.find(nombreInicio, posicion)
            if (posicionInicio > -1):
                posicionInicio += len(nombreInicio)
                posicionFin = cadena2.find(nombreFin, posicionInicio)
                if(posicionFin>-1):
                    respuesta = cadena[posicionInicio:posicionFin]
        else:
            posicionInicio = cadena.find(nombreInicio, posicion)
            if (posicionInicio > -1):
                posicionInicio += len(nombreInicio)
                posicionFin = cadena.find(nombreFin, posicionInicio)
                if(posicionFin>-1):
                    respuesta = cadena[posicionInicio:posicionFin]
        return respuesta

    def ExtraerContenidoEntreTag(self, cadena, posicion, nombreInicio, nombreFin, sensitivo=False):
        respuesta = list()
        if(sensitivo):
            cadena2 = cadena.lower()
            nombreInicio = nombreInicio.lower()
            nombreFin=nombreFin.lower()
            posicionInicio = cadena2.find(nombreInicio, posicion)
            if (posicionInicio > -1):
                posicionInicio += len(nombreInicio)
                posicionFin = cadena2.find(nombreFin, posicionInicio)
                if(posicionFin>-1):
                    posicion = posicionFin + len(nombreFin)
                    respuesta = [posicion, cadena[posicionInicio:posicionFin]]
        else:
            posicionInicio = cadena.find(nombreInicio, posicion)
            if (posicionInicio > -1):
                posicionInicio += len(nombreInicio)
                posicionFin = cadena.find(nombreFin, posicionInicio)
                if(posicionFin>-1):
                    posicion = posicionFin + len(nombreFin)
                    respuesta = [posicion, cadena[posicionInicio:posicionFin]]
        return respuesta

class EnSUNAT(object):
    def __init__(self):
        self.TipoRespuesta = 0
        self.MensajeRespuesta = ""
        self.RUC = ""
        self.TipoContribuyente = ""
        self.NombreComercial = ""
        self.FechaInscripcion = ""
        self.FechaInicioActividades = ""
        self.EstadoContribuyente = ""
        self.CondicionContribuyente = ""
        self.DomicilioFiscal = ""
        self.SistemaEmisionComprobante = ""
        self.ActividadComercioExterior = ""
        self.SistemaContabilidiad = ""
        self.ActividadesEconomicas = ""
        self.ComprobantesPago = ""
        self.SistemaEmisionElectrónica = ""
        self.EmisorElectrónicoDesde = ""
        self.ComprobantesElectronicos = ""
        self.AfiliadoPLEDesde = ""
        self.Padrones = ""
        self.RepresentantesLesgales = []
        self.LoacalesAnexos = []