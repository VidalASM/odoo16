# -*- coding: utf-8 -*-
from odoo import models, fields, api

class DocumentTag(models.Model):

    _inherit = "documents.tag"

    @api.model
    def _get_tags(self, domain, folder_id):
        """
        fetches the tag and facet ids for the document selector (custom left sidebar of the kanban view)
        """
        documents = self.env['documents.document'].search(domain)
        # folders are searched with sudo() so we fetch the tags and facets from all the folder hierarchy (as tags
        # and facets are inherited from ancestor folders).
        # folders = self.env['documents.folder'].sudo().search([('parent_folder_id', 'parent_of', folder_id)])
        folders = self.env['documents.folder'].sudo().search([])
        self.flush(['sequence', 'name', 'facet_id'])
        self.env['documents.facet'].flush(['sequence', 'name', 'tooltip'])
        query = """
                SELECT  facet.sequence AS group_sequence,
                        facet.id AS group_id,
                        facet.tooltip AS group_tooltip,
                        documents_tag.sequence AS sequence,
                        documents_tag.id AS id,
                        COUNT(rel.documents_document_id) AS __count
                FROM documents_tag
                    JOIN documents_facet facet ON documents_tag.facet_id = facet.id
                        AND facet.folder_id = ANY(%s)
                    LEFT JOIN document_tag_rel rel ON documents_tag.id = rel.documents_tag_id
                        AND rel.documents_document_id = ANY(%s)
                GROUP BY facet.sequence, facet.name, facet.id, facet.tooltip, documents_tag.sequence, documents_tag.name, documents_tag.id
                ORDER BY facet.sequence, facet.name, facet.id, facet.tooltip, documents_tag.sequence, documents_tag.name, documents_tag.id
            """
        params = [
            list(folders.ids),
            list(documents.ids),  # using Postgresql's ANY() with a list to prevent empty list of documents
        ]
        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()

        # Translating result
        groups = self.env['documents.facet'].browse({r['group_id'] for r in result})
        group_names = {group['id']: group['name'] for group in groups}

        tags = self.env['documents.tag'].browse({r['id'] for r in result})
        tags_names = {tag['id']: tag['name'] for tag in tags}

        for r in result:
            r['group_name'] = group_names.get(r['group_id'])
            r['display_name'] = tags_names.get(r['id'])

        return result
