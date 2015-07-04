from django_prometheus.model_gauge import QuerySetGauge
from django_prometheus.testutils import PrometheusTestCaseMixin
from django.test import TestCase
from testapp.models import Ingredient, Recipe


class TestQuerySetGauge(PrometheusTestCaseMixin, TestCase):
    """Test QuerySetGauge."""

    def setUp(self):
        spaghetti = Ingredient(name='spaghetti')
        spaghetti.save()
        tomato = Ingredient(name='tomato')
        tomato.save()
        beef = Ingredient(name='beef')
        beef.save()
        carrot = Ingredient(name='carrot')
        carrot.save()
        bolognese = Recipe(name='bolognese', country='IT')
        bolognese.save()
        bolognese.ingredients.add(spaghetti, tomato, beef)
        boeuf_carrottes = Recipe(name='boeuf carrottes', country='FR')
        boeuf_carrottes.save()
        boeuf_carrottes.ingredients.add(carrot, beef)
        cote_de_boeuf = Recipe(name='cote de boeuf', country='FR')
        cote_de_boeuf.save()
        cote_de_boeuf.ingredients.add(beef)

    def test_querysetgauge(self):
        qs = Recipe.objects
        QuerySetGauge(qs, 'recipe_by_country_total',
                      'Number of recipes by country', ['country'])

        self.assertMetricEquals(
            2, 'recipe_by_country_total', country='FR')
        self.assertMetricEquals(
            1, 'recipe_by_country_total', country='IT')

    def test_related_model(self):
        qs = Recipe.objects
        QuerySetGauge(qs, 'ingredients_by_recipe_total',
                      'Number of ingredients by recipe', ['name'],
                      count_by='ingredients')

        self.assertMetricEquals(
            3, 'ingredients_by_recipe_total', name='bolognese')
        self.assertMetricEquals(
            1, 'ingredients_by_recipe_total', name='cote de boeuf')
        self.assertMetricEquals(
            2, 'ingredients_by_recipe_total', name='boeuf carrottes')

    def test_multiple_labels(self):
        qs = Recipe.objects
        QuerySetGauge(qs, 'ingredients_by_recipe_country_total',
                      'Number of ingredients by recipe and country',
                      ['name', 'country'], count_by='ingredients')

        self.assertMetricEquals(3, 'ingredients_by_recipe_country_total',
                                name='bolognese', country='IT')
        self.assertMetricEquals(1, 'ingredients_by_recipe_country_total',
                                name='cote de boeuf', country='FR')
        self.assertMetricEquals(2, 'ingredients_by_recipe_country_total',
                                name='boeuf carrottes', country='FR')