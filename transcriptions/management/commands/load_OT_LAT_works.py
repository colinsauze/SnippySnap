from django.core.management.base import BaseCommand, CommandError
from transcriptions.models import Work


class Command(BaseCommand):
    #TODO: finish this script 
    def handle(self, *args, **options):
        OT_works_data = {
            'Gen': {'name': 'Genesis', 'abbreviation': 'Gen', 'book_number': 1},
            'Exod': {'name': 'Exodus', 'abbreviation': 'Exod', 'book_number': 2},
            'Lev': {'name': 'Leviticus', 'abbreviation': 'Lev', 'book_number': 3},
            'Num': {'name': 'Numbers', 'abbreviation': 'Num', 'book_number': 4},
            'Deut': {'name': 'Deuteronomy', 'abbreviation': 'Deut', 'book_number': 5},
            'Josh': {'name': 'Joshua', 'abbreviation': 'Josh', 'book_number': 6},
            'Judg': {'name': 'Judges', 'abbreviation': 'Judg', 'book_number': 7},
            'Ruth' : {'name': 'Ruth', 'abbreviation': 'Ruth', 'book_number': 8},
            '1Sam' : {'name': '1 Samuel (1 Kings)', 'abbreviation': '1Sam', 'book_number': 9},
    #   {'id': 'OT_2Sam', 'corpus': 'OT', 'name': '2 Samuel (2 Kings)', 'abbreviation': '2Sam', 'book_number': 110},
    #   {'id': 'OT_1Kgs', 'corpus': 'OT', 'name': '1 Kings (3 Kings)', 'abbreviation': '1Kgs', 'book_number': 111},
    #   {'id': 'OT_2Kgs', 'corpus': 'OT', 'name': '2 Kings (4 Kings)', 'abbreviation': '2Kgs', 'book_number': 112},
    #   {'id': 'OT_1Chr', 'corpus': 'OT', 'name': '1 Chronicles (1 Paralipomenon)', 'abbreviation': '1Chr', 'book_number': 113},
    #   {'id': 'OT_2Chr', 'corpus': 'OT', 'name': '2 Chronicles (2 Paralipomenon)', 'abbreviation': '2Chr', 'book_number': 114},
    #   {'id': 'OT_Ezra', 'corpus': 'OT', 'name': 'Ezra', 'abbreviation': 'Ezra', 'book_number': 115},
    #   {'id': 'OT_Neh', 'corpus': 'OT', 'name': 'Nehemiah', 'abbreviation': 'Neh', 'book_number': 116},
    #   {'id': 'OT_Esth', 'corpus': 'OT', 'name': 'Tobit (Tobias)', 'abbreviation': 'Esth', 'book_number': 117},
    #   {'id': 'OT_B118', 'corpus': 'OT', 'name': 'Judith', 'book_number': 118},
    #   {'id': 'OT_B119', 'corpus': 'OT', 'name': 'Esther', 'book_number': 119},
    #   {'id': 'OT_B120', 'corpus': 'OT', 'name': 'Job', 'book_number': 120},
    #   {'id': 'OT_B121', 'corpus': 'OT', 'name': 'Psalms', 'book_number': 121},
    #   {'id': 'OT_B122', 'corpus': 'OT', 'name': 'Canticles (Odes)', 'book_number': 122},
    #   {'id': 'OT_B123', 'corpus': 'OT', 'name': 'Proverbs', 'book_number': 123},
    #   {'id': 'OT_B124', 'corpus': 'OT', 'name': 'Ecclesiastes', 'book_number': 124},
    #   {'id': 'OT_B125', 'corpus': 'OT', 'name': 'Song of Songs (Canticum canticorum)', 'book_number': 125},
    #   {'id': 'OT_B126', 'corpus': 'OT', 'name': 'Wisdom (Sapientia)', 'book_number': 126},
    #   {'id': 'OT_B127', 'corpus': 'OT', 'name': 'Sirach (Ecclesiasticus)', 'book_number': 127},
    #   {'id': 'OT_B128', 'corpus': 'OT', 'name': 'Isaiah', 'book_number': 128},
    #   {'id': 'OT_B129', 'corpus': 'OT', 'name': 'Jeremiah', 'book_number': 129},
    #   {'id': 'OT_B130', 'corpus': 'OT', 'name': 'Lamentations', 'book_number': 130},
    #   {'id': 'OT_B131', 'corpus': 'OT', 'name': 'Baruch', 'book_number': 131},
    #   {'id': 'OT_B132', 'corpus': 'OT', 'name': 'Ezekiel', 'book_number': 132},
    #   {'id': 'OT_B133', 'corpus': 'OT', 'name': 'Daniel', 'book_number': 133},
    #   {'id': 'OT_B134', 'corpus': 'OT', 'name': 'Hosea (Osee)', 'book_number': 134},
    #   {'id': 'OT_B135', 'corpus': 'OT', 'name': 'Joel', 'book_number': 135},
    #   {'id': 'OT_B136', 'corpus': 'OT', 'name': 'Amos', 'book_number': 136},
    #   {'id': 'OT_B137', 'corpus': 'OT', 'name': 'Obadiah (Abdias)', 'book_number': 137},
    #   {'id': 'OT_B138', 'corpus': 'OT', 'name': 'Jonah', 'book_number': 138},
    #   {'id': 'OT_B139', 'corpus': 'OT', 'name': 'Micah', 'book_number': 139},
    #   {'id': 'OT_B140', 'corpus': 'OT', 'name': 'Nahum', 'book_number': 140},
    #   {'id': 'OT_B141', 'corpus': 'OT', 'name': 'Habakkuk', 'book_number': 141},
    #   {'id': 'OT_B142', 'corpus': 'OT', 'name': 'Zephaniah (Sophonias)', 'book_number': 142},
    #   {'id': 'OT_B143', 'corpus': 'OT', 'name': 'Haggai', 'book_number': 143},
    #   {'id': 'OT_B144', 'corpus': 'OT', 'name': 'Zechariah (Zacharias)', 'book_number': 144},
    #   {'id': 'OT_B145', 'corpus': 'OT', 'name': 'Malachi', 'book_number': 145},
    #   {'id': 'OT_B146', 'corpus': 'OT', 'name': '1 Maccabees', 'book_number': 146},
    #   {'id': 'OT_B147', 'corpus': 'OT', 'name': '2 Maccabees', 'book_number': 147},
    #   {'id': 'OT_B148', 'corpus': 'OT', 'name': '3 Maccabees', 'book_number': 148},
    #   {'id': 'OT_B149', 'corpus': 'OT', 'name': '4 Maccabees', 'book_number': 149},
    #   {'id': 'OT_B150', 'corpus': 'OT', 'name': 'Prayer of Manasseh (Oratio Manasse)', 'book_number': 150},
    #   {'id': 'OT_B151', 'corpus': 'OT', 'name': '1 Esdras', 'book_number': 151},
    #   {'id': 'OT_B152', 'corpus': 'OT', 'name': '2 Esdras', 'book_number': 152},
    #   {'id': 'OT_B153', 'corpus': 'OT', 'name': 'Epistle of Jeremiah', 'book_number': 153},
    #   {'id': 'OT_B154', 'corpus': 'OT', 'name': 'Psalms of Solomon', 'book_number': 154},
    #   {'id': 'OT_B155', 'corpus': 'OT', 'name': 'Additions to Esther', 'book_number': 155},
    #   {'id': 'OT_B156', 'corpus': 'OT', 'name': 'Song of the Three Children', 'book_number': 156},
    #   {'id': 'OT_B157', 'corpus': 'OT', 'name': 'Story of Susana', 'book_number': 157},
    #   {'id': 'OT_B158', 'corpus': 'OT', 'name': 'Bel and the Dragon', 'book_number': 158},    #
    #   {'id': 'OT_B159', 'corpus': 'OT', 'name': 'Psalm 151', 'book_number': 159},

        }


        for entry in OT_works_data:

            OT_works_data[entry]['corpus'] = 'OT'
            OT_works_data[entry]['language'] = 'lat'
            OT_works_data[entry]['identifier'] = 'OT_LAT_%s' % OT_works_data[entry]['abbreviation']
            w = Work(**OT_works_data[entry])

            #check if we have an existing entry - if so we must ensure we keep the pk as other things link to this
            try:
                existing = Work.objects.get(identifier=OT_works_data[entry]['identifier'])
                w.id = existing.id
            except:
                pass
            w.save()
