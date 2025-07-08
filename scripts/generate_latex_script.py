from pathlib import Path
import argparse


class LatexFileGenerator():
    """
    Parameters
    - path_to_root_dir: the root directory must have the following structure

    Your_custom_class_root_folder
    ├── AbilityCards
        ├── (all your cards, either .jpg or .png - they can have any name)
    ├── AMD
        ├── (all your AMDS, either .jpg or .png - they can have any name)
    ├── NON_AMD
        ├── (all your NON_AMD perk cards, either .jpg or .png - they can have any name)
    ├── ability_card_back.png
    ├── amd_back.png
    ├── non_amd_back.png
    ├── character_token.png
    ├── character_mat.png
    ├── character_mat_back.png
    ├── character_mini.png
    ├── character_sheet.png

    - output_path: path and name for the generated LaTeX file
    - is_a4: if True, the output file will be in A4 format, else it will be in US letter format
    - has_bleed: leave this to True if the cards already have bleed, and change it to False if they don't.
        Cards will be resized accordingly so that the end-cards (cards with bleed cut out and cards without bleed)
        have the same physical size.
    """

    def __init__(self,
                 path_to_root_dir: str,
                 output_path: str,
                 is_a4: bool,
                 has_bleed: bool = True):
        self.path_to_root_dir = Path(path_to_root_dir)
        self.output_path = Path(output_path)
        self.is_a4 = is_a4
        self.has_bleed = has_bleed
        self.rotate_amd_cards = True
        self.check_root_dir_consistency()

    def sanitize_path(p: str) -> str:
        return p.replace("\\", "/").replace(" ", "\\ ")

    def check_root_dir_consistency(self):
        """
        Raises an error is the root directory doesn't have the correct structure.
        """
        if not Path(self.path_to_root_dir / "AbilityCards").exists():
            raise ValueError(f"Missing folder with the name AbilityCards in {self.path_to_root_dir}")
        if not Path(self.path_to_root_dir / "AMD").exists():
            raise ValueError(f"Missing folder with the name AMD in {self.path_to_root_dir}")

        for filename in ["ability_card_back", "amd_back", "non_amd_back", "character_token", "character_mat",
                         "character_mat_back", "character_mini", "character_sheet"]:
            if not Path(self.path_to_root_dir / filename).with_suffix(".jpg").exists() and not Path(
                    self.path_to_root_dir / filename).with_suffix(".png").exists():
                raise ValueError(f"Missing file {filename} (JPG or PNG format) in {self.path_to_root_dir}")

    def generate_latex_file(self):
        latex_code = self.header()
        # Ability cards
        card_paths = list(Path(self.path_to_root_dir / "AbilityCards").glob("*.jpg")) + list(
            Path(self.path_to_root_dir / "AbilityCards").glob("*.png"))
        card_paths.sort()
        card_back_path = Path(self.path_to_root_dir / "ability_card_back.jpg")
        if not card_back_path.exists():
            card_back_path = Path(self.path_to_root_dir / "ability_card_back.png")
        card_paths = [LatexFileGenerator.sanitize_path(str(p)) for p in (card_paths)]
        card_back_path = LatexFileGenerator.sanitize_path(str(card_back_path))
        latex_code += self.ability_cards([str(c) for c in card_paths], str(card_back_path))

        # #AMD
        amd_paths = list(Path(self.path_to_root_dir / "AMD").glob("*.jpg")) + list(
            Path(self.path_to_root_dir / "AMD").glob("*.png"))
        amd_paths.sort()
        amd_back_path = Path(self.path_to_root_dir / "amd_back.jpg")
        if not amd_back_path.exists():
            amd_back_path = Path(self.path_to_root_dir / "amd_back.png")
        amd_backs = [amd_back_path for _ in amd_paths];

        # NON_AMD
        non_amd_paths = list(Path(self.path_to_root_dir / "NON_AMD").glob("*.jpg")) + \
                        list(Path(self.path_to_root_dir / "NON_AMD").glob("*.png"))
        non_amd_paths.sort()
        non_amd_back_path = Path(self.path_to_root_dir / "non_amd_back.jpg")
        if not non_amd_back_path.exists():
            non_amd_back_path = Path(self.path_to_root_dir / "non_amd_back.png")
        non_amd_backs = [non_amd_back_path for _ in non_amd_paths]

        # Characater tokens
        token_path = Path(self.path_to_root_dir / "character_token.jpg")
        if not token_path.exists():
            token_path = Path(self.path_to_root_dir / "character_token.png")
        token_path = LatexFileGenerator.sanitize_path(str(token_path))

        # Arranging amd and non_amd
        all_amd = amd_paths + non_amd_paths
        all_backs = amd_backs + non_amd_backs

        all_amd_cards = [LatexFileGenerator.sanitize_path(str(p)) for p in (all_amd + all_backs)]
        # TODO: I would move the tokens to be alongside the mat and mini
        #  since these are more likely to be printed onto sticky paper
        latex_code += self.amd_cards([str(c) for c in all_amd_cards], str(token_path))

        # Character mat and mini
        mat_mini_paths = []
        for filename in ["character_mat", "character_mat_back", "character_mini"]:
            jpg_file = Path(self.path_to_root_dir / filename).with_suffix(".jpg")
            if not jpg_file.exists():
                jpg_file = Path(self.path_to_root_dir / filename).with_suffix(".png")
            mat_mini_paths.append(jpg_file)
        mat_mini_paths = [LatexFileGenerator.sanitize_path(str(p)) for p in (mat_mini_paths)]
        latex_code += self.character_mat(str(mat_mini_paths[0]), str(mat_mini_paths[1]), str(mat_mini_paths[2]))

        # Character sheet
        sheet = Path(self.path_to_root_dir / "character_sheet.jpg")
        if not sheet.exists():
            sheet = Path(self.path_to_root_dir / "character_sheet.png")
        sheet = LatexFileGenerator.sanitize_path(str(sheet))
        latex_code += self.character_sheet(str(sheet))
        latex_code += self.end_document()

        with open(self.output_path, "w") as f:
            f.write(latex_code)

    def header(self):
        header_string = r"\documentclass[12pt,"
        if self.is_a4:
            header_string += "a4paper"
        else:
            header_string += "letterpaper"
        return header_string + r""",notitlepage,landscape]{article}
\usepackage{graphicx}
\usepackage{subcaption}
\usepackage{pdflscape}
\usepackage[space]{grffile}

\pagenumbering{gobble}

\addtolength{\topmargin}{-3.4cm}
\begin{document}

"""

    def end_document(self):
        return r"\end{document}"

    def character_sheet(self, path_to_sheet: str):
        res = r"""\clearpage

\begin{figure}[ht]
\centering
\makebox[1\textwidth]{
\includegraphics[height=14cm]{""" + path_to_sheet + r"""}\hspace{0cm}%
\includegraphics[height=14cm]{""" + path_to_sheet + r"""}
}
\end{figure}

"""
        return res + res  # Back of the character sheet is the same as the front for now

    def amd_cards_one_page(self,
                           amd_paths: list[str],
                           token_path: str | None = None):
        """
        Helper function to generate latex code for a single AMD page. Holds up 10 cards
        in two rows of 5. Character tokens can also be added
        """
        res = r"""\begin{figure}[ht]
  \centering
\setkeys{Gin}{width=6.9cm}
\makebox[1\textwidth]{
"""
        add_rotation = ""
        # TODO: add no rotation case?
        if self.rotate_amd_cards:
            add_rotation = "angle=90, "
        for i in range(len(amd_paths)):
            # TODO: need to adjust this; provided width is 4.3cm, but we already have a height issue,
            #  and this will make it worse?
            res += r"  \includegraphics[" + add_rotation + r"width=4.4cm]{" + amd_paths[i] + r"}"
            if i != len(amd_paths) - 1 and i != 4:
                res += r"\hspace{0cm}%" + "\n"
            if i == 4:  # create new line of AMDs
                res += r"""
}
\makebox[\textwidth]{
"""

        if token_path is not None:
            res += r"""
}
\makebox[1\textwidth]{""" + "\n"
            for i in range(5):
                res += r"  \includegraphics[width=1.45cm]{" + token_path + r"}"
                res += r"\hspace{0cm}%" + "\n"
                res += r"  \scalebox{-1}[1]{\includegraphics[width=1.45cm]{" + token_path + r"}}"
                if i != 9:
                    res += r"\hspace{0cm}%" + "\n"
        res += r"""
}
\end{figure}

\clearpage

"""
        return res

    def amd_cards(self, amd_paths: list[str], character_token_path: str):
        res = ""
        n = len(amd_paths)
        cards_per_page = 10
        num_pages = (n + cards_per_page - 1) // cards_per_page  # ceil division

        for i in range(num_pages):
            amds_in_page = amd_paths[cards_per_page * i: cards_per_page * (i + 1)]
            if i != num_pages - 1:
                res += self.amd_cards_one_page(amds_in_page)
            else:
                # Last page: also add character tokens
                res += self.amd_cards_one_page(amds_in_page, character_token_path)
        return res

    def ability_cards_one_page(self,
                               card_paths: list[str]):
        """
        Helper function to generate latex code for a single page. Holds up
        to a maximum of 8 ability cards, or 6 if using US Letter format with bleed.
        """
        res = r"""\begin{figure}[ht]
  \centering
\setkeys{Gin}{width="""
        # Make sure the final cards have the same physical size (ie cards printed with bleed, but with bleed cut out, and cards printed without bleed)
        if self.has_bleed:
            res += "6.99cm"
        else:
            res += "6.35cm"
        res += r"""}
\makebox[1\textwidth]{
"""
        cards_per_line = 4
        if not self.is_a4 and self.has_bleed:
            cards_per_line = 3
        for i in range(len(card_paths)):
            res += r"   \includegraphics{" + card_paths[i] + r"}"
            if i != len(card_paths) - 1 and i != cards_per_line - 1:
                res += r"\hspace{0cm}%" + "\n"
            if i == cards_per_line - 1:
                res += r"""
}
\makebox[\textwidth]{
"""
        # end of the for loop
        res += r"""
}
\end{figure}

\clearpage

"""
        return res

    def ability_cards(self,
                      card_paths: list[str],  # list of paths to the cards
                      ability_card_back: str):

        cards_per_line = 4
        if not self.is_a4 and self.has_bleed:
            cards_per_line = 3
        res = ""
        # Subdivide card_paths into group of 6 or 8 cards if possible
        for i in range(len(card_paths) // (2 * cards_per_line) + 1):
            cards_in_page = card_paths[2 * cards_per_line * i:2 * cards_per_line * (i + 1)]
            res += self.ability_cards_one_page(cards_in_page)
            # Ability card background
            res += self.ability_cards_one_page([ability_card_back for _ in range(len(cards_in_page))])
        return res

    def character_mat(self,
                      mat_front_path: str,
                      mat_back_path: str,
                      characer_mini_path: str):
        res = r"""\begin{figure}[ht]
\centering
\makebox[1\textwidth]{
\includegraphics[width=14.5cm,height=9.5cm]{""" + mat_front_path + r"""}\hspace{0cm}%
}
\makebox[1\textwidth]{
	\includegraphics[width=4cm]{""" + characer_mini_path + r"""}
}
\end{figure}

\clearpage

\begin{figure}[ht]
\centering
\makebox[1\textwidth]{
\includegraphics[width=14.5cm,height=9.5cm]{""" + mat_back_path + r"""}%
}
\makebox[1\textwidth]{
\scalebox{-1}[1]{\includegraphics[width=4cm]{""" + characer_mini_path + r"""}}\hspace{0cm}%
}
\end{figure}

\clearpage"""
        return res


argparser = argparse.ArgumentParser()
argparser.add_argument("path_to_root_dir", action="store", metavar="",
                       help="path to the directory containing all images of the custom class")
argparser.add_argument("output_path", action="store", metavar="",
                       help="path to the output LaTeX file.")
argparser.add_argument("--is_A4", action=argparse.BooleanOptionalAction, default=True,
                       help='if the PNP file should be A4 (True) or US_letter (False). Default is A4')
argparser.add_argument("--with_bleed", action=argparse.BooleanOptionalAction, default=True,
                       help="if the ability cards don't have bleed, change this to False.")
arguments = argparser.parse_args()

filegen = LatexFileGenerator(arguments.path_to_root_dir,
                             arguments.output_path,
                             arguments.is_A4,
                             arguments.with_bleed)
filegen.generate_latex_file()
