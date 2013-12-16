import os
import json
import codecs

from base import BaseTextFormat


class JSONFormat(BaseTextFormat):

    extension = 'json'

    @classmethod
    def populate_argument_parser(cls, parser):
        group = parser.add_argument_group("JSON format options")

        group.add_argument("--json",
                           dest="json_dir",
                           nargs='?',
                           const=True,
                           default=os.environ.get('GLUE_JSON', False),
                           metavar='DIR',
                           help="Generate JSON files and optionally where")

        group.add_argument("--json-format",
                   dest="json_format",
                   metavar='NAME',
                   type=unicode,
                   default=os.environ.get('GLUE_JSON_FORMAT', 'array'),
                    choices=['array', 'hash'],
                   help=("JSON structure format (array, hash)"))

    def needs_rebuild(self):
        for ratio in self.sprite.config['ratios']:
            json_path = self.output_path(ratio)
            if os.path.exists(json_path):
                with codecs.open(json_path, 'r', 'utf-8-sig') as f:
                    try:
                        data = json.loads(f.read())
                        assert data['meta']['hash'] == self.sprite.hash
                    except Exception:
                        continue
            return True
        return False

    def get_context(self):
        context = super(JSONFormat, self).get_context()

        frames = {i['filename']: i for i in context['images']}
        del context['images']
        data = {'meta': context}

        if self.sprite.config['json_format'] == 'array':
            data['frames'] = frames.values()
        else:
            data['frames'] = frames

        return data

    def render(self, *args, **kwargs):
        return json.dumps(self.get_context())