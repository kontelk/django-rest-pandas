from rest_framework import serializers
from pandas import DataFrame


class PandasBaseSerializer(serializers.Serializer):
    """
    Transforms dataset into a dataframe and appies an index
    """
    read_only = True

    def get_index(self, dataframe):
        return None

    def get_dataframe(self, data):
        dataframe = DataFrame(data)
        index = self.get_index(dataframe)
        if index:
            dataframe = dataframe.set_index(index)
        else:
            # Name auto-index column to ensure valid CSV output
            dataframe.index.name = 'row'
        return dataframe

    def filter_dataframe(self, dataframe):
        view = self.context.get('view', None)
        if view and hasattr(view, 'filter_dataframe'):
            return self.context['view'].filter_dataframe(dataframe)
        return dataframe

    @property
    def data(self):
        data = super(PandasBaseSerializer, self).data
        if data:
            dataframe = self.get_dataframe(data)
            return self.filter_dataframe(dataframe)
        else:
            return DataFrame([])


class PandasSimpleSerializer(PandasBaseSerializer):
    """
    Simple serializer for non-model (simple) views
    """
    def get_default_fields(self):
        if not self.object:
            return {}
        return {
            name: serializers.Field()
            for name in self.object[0].keys()
        }


class PandasSerializer(PandasBaseSerializer, serializers.ModelSerializer):
    """
    Serializer for model views.
    """
    def get_index(self, dataframe):
        return ['id']
