import pathlib
import attr
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Language
from pylexibank import FormSpec


@attr.s
class CustomLanguage(Language):
    Sources = attr.ib(default=None)

class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "pachechibchan"
    language_class = CustomLanguage
    form_spec = FormSpec(separators="~;,/", missing_data=["∅"], first_form_only=True)

    def cmd_makecldf(self, args):
        # add bib
        args.writer.add_sources()
        args.log.info("added sources")

        # add concept
        concepts = {}
        for concept in self.concepts:
            idx = concept["NUMBER"] + "_" + slug(concept["ENGLISH"])
            args.writer.add_concept(
                    ID=idx, 
                    Name=concept["ENGLISH"]
                    )
            concepts[concept["ENGLISH"]] = idx
        args.log.info("added concepts")

        # add language
        languages = args.writer.add_languages(lookup_factory="Name")
        args.log.info("added languages")

        # read in data
        data = self.raw_dir.read_csv(
            "data.tsv", delimiter="\t", dicts=True
        )
        for row in pb(data[1:], desc="cldfify", total=len(data[1:])):
            new_concept = row["English"].strip()
            if new_concept.strip():
                concept = new_concept
            else:
                pass
            for language in self.languages:
                entry = row[language["ID"]]
                if entry.strip():
                    args.writer.add_forms_from_value(
                        Language_ID=language["ID"],
                        Parameter_ID=concepts[concept],
                        Value=entry,
                        )

