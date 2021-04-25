# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

import json

from collections import OrderedDict
from copy import deepcopy

from formiodata.builder import Builder


class Form:

    def __init__(self, form_json, builder=None, builder_schema_json=None, lang='en'):
        """
        @param form_json
        @param builder Builder
        @param builder_schema
        @param lang
        """
        if isinstance(form_json, dict):
            self.form = form_json
        else:
            self.form = json.loads(form_json)

        self.builder = builder
        self.builder_schema_json = builder_schema_json
        self.lang = lang

        if self.builder and self.builder_schema_json:
            raise Exception("Constructor accepts either builder or builder_schema_json.")

        if self.builder:
            assert isinstance(self.builder, Builder)
        elif self.builder_schema_json:
            assert isinstance(self.builder_schema_json, str)
        else:
            raise Exception("Provide either the argument: builder or builder_schema_json.")

        if self.builder is None and self.builder_schema_json:
            self.set_builder_by_builder_schema_json()

        self.components = {}
        self.load_components()
        self.data = FormData(self)

    def render(self):
        return FormRenderer(self)

    def set_builder_by_builder_schema_json(self):
        self.builder = Builder(self.builder_schema_json, self.lang)

    def load_components(self):
        # TODO: Make recursive(?)
        for key, component in self.builder.form_components.items():
            # Rather lazy check, but sane.
            # if not self.form.get(key):
            #     continue
            # replaced with default value and fast
            raw_value = self.form.get(key, component.defaultValue)
            component.component_owner = self.builder
            component.value = raw_value
            component.raw_value = raw_value
            self.components[key] = component

    def render_components(self, force=False):
        for key, component in self.components.items():
            if force or component.html_component == "":
                component.render()


class FormRenderer:

    def __init__(self, form):
        self.form = form
        self.builder = form.builder
        self.load_components()

    def load_components(self):
        """ Loads the components (tree) to render, with values
        (data) and obtaining the tree by creating all sub-components
        e.g. in layout and datagrid. """
        self.builder.load_components()

    @property
    def components(self):
        return self.builder.components

    @property
    def component_ids(self):
        return self.builder.component_ids

class FormData:

    def __init__(self, form):
        self._form = form

    def __getattr__(self, key):
        return self._form.components.get(key)
