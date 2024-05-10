from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _tags_invisible_per_country(self, arch, view, tags, countries):
        """
        Modifies the visibility of specified XML tags in the view's arch XML based on the country of the current company.

        Args:
            arch (etree._Element): The arch XML element of the view.
            view (etree._Element): The view XML element.
            tags (list): List of tag names or tuples representing Xpath queries for tags to make invisible.
            countries (list): List of country references to check against the current company's country.

        Returns:
            Tuple[etree._Element, etree._Element]: The modified arch and view elements.

        This function checks if the country of the current company is in the provided list of countries.
        If true, it returns the original arch and view without modification. Otherwise, it iterates through
        the specified tags and makes corresponding elements invisible in the arch XML.

        Example:
            Assuming tags = ['ubigeo', ('group', 'extended_info')], countries = [self.env.ref('base.pe')],
            and the current company's country is 'Peru', the function will modify the arch XML to make
            elements with Xpath queries "//field[@name='ubigeo']" and "//group[@name='extended_info']"
            invisible.

        Note:
            This function is intended to be called from the '_get_view' method of an Odoo model.

        """
        country_company = self.env.company.country_id in countries
        if country_company:
            return arch, view
        for tag in tags:
            if isinstance(tag, tuple):
                value = "//{}[@name='{}']".format(tag[0], tag[1])
            else:
                value = "//field[@name='{}']".format(tag)
            for node in arch.xpath(value):
                node.set('invisible', '1')
        return arch, view
