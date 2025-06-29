# morlus-converter\main.py

import tkinter as tk
from tkinter import filedialog, messagebox

import pandas as pd


class CodeMapper:
    def __init__(self, filepath, use_header_line4=True):
        self.filepath = filepath
        self.use_header_line4 = use_header_line4
        self.df = self.load_dataset()

    def load_dataset(self):
        df = pd.read_csv(self.filepath, sep="\t", header=None, dtype=str).fillna("None")
        if self.use_header_line4:
            header = df.iloc[3].tolist()
            df = df[4:].copy()
            df.columns = header
        else:
            df.columns = ["COL_" + str(i) for i in range(df.shape[1])]
            df = df[4:].copy()
        return df

    def build_mapping(self, lang_mode, char_types, code_column_name):
        mappings = {}
        filtered_df = self.df.copy()

        for _, row in filtered_df.iterrows():
            for col in char_types:
                char = row[col]
                code = row[code_column_name]
                if char != "None" and code != "None":
                    mappings[char] = code
        return mappings

    def build_reverse_mapping(self, lang_mode, char_types, code_column_name):
        mappings = {}
        filtered_df = self.df.copy()

        for _, row in filtered_df.iterrows():
            for col in char_types:
                char = row[col]
                code = row[code_column_name]
                if char != "None" and code != "None":
                    mappings[code] = char
        return mappings


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("符丁 ⇄ 符号 変換ツール")
        self.geometry("600x550+0+0") # ウィンドウ出現位置を画面左上に固定

        self.mapper = None
        self.kana_preference = tk.StringVar(value="hiragana")  # ひらがな／カタカナ選択
        self.setup_widgets()

    def setup_widgets(self):
        self.file_button = tk.Button(self, text="データセット選択", command=self.load_file)
        self.file_button.pack()

        # 変換設定
        self.convert_settings_labelframe = tk.LabelFrame(self, text="変換の設定")
        
        # 一段目の配置フレーム
        self.row1_frame = tk.Frame(self.convert_settings_labelframe)

        # 文章言語の選択
        self.lang_mode = tk.StringVar(value="JP")
        self.lang_mode_labelframe = tk.LabelFrame(self.row1_frame, text="符丁文章の入力言語")
        tk.Radiobutton(self.lang_mode_labelframe, text="和文", variable=self.lang_mode, value="JP").pack(side=tk.LEFT)
        tk.Radiobutton(self.lang_mode_labelframe, text="欧文", variable=self.lang_mode, value="US").pack(side=tk.LEFT)
        self.lang_mode_labelframe.pack(side='left', padx=5)

        # 変換する符号種別の選択
        self.code_type = tk.StringVar(value="V7")
        self.code_type_labelframe = tk.LabelFrame(self.row1_frame, text="符丁文章を変換する符号の種別")
        tk.Radiobutton(self.code_type_labelframe, text="V7符号", variable=self.code_type, value="V7").pack(side=tk.LEFT)
        tk.Radiobutton(self.code_type_labelframe, text="標準モールス", variable=self.code_type, value="morse").pack(side=tk.LEFT)
        self.code_type_labelframe.pack(side='left', padx=5)

        # 変換方向の選択
        self.convert_mode = tk.StringVar(value="to_code")
        self.convert_mode_labelframe = tk.LabelFrame(self.row1_frame, text="文章文字列の変換方向")
        tk.Radiobutton(self.convert_mode_labelframe, text="符丁→符号", variable=self.convert_mode, value="to_code").pack(side=tk.LEFT)
        tk.Radiobutton(self.convert_mode_labelframe, text="符号→符丁", variable=self.convert_mode, value="to_text").pack(side=tk.LEFT)
        self.convert_mode_labelframe.pack(side='left', padx=5)

        # 一段目の配置フレームレイアウトマネージャー
        self.row1_frame.pack(padx=5)

        # 二段目の配置フレーム
        self.row2_frame = tk.Frame(self.convert_settings_labelframe)

        # 符号文章内での符号文字列の区切りに利用する任意の文字列（デフォルトでは"全角感嘆符2文字+半角空白記号"）
        # 和文逆引きでのひらがな／カタカナ選択
        self.kana_frame = tk.LabelFrame(self.row2_frame, text="和文の逆引き対象文字種")
        tk.Radiobutton(self.kana_frame, text="ひらがな優先", variable=self.kana_preference, value="hiragana").pack(side=tk.LEFT)
        tk.Radiobutton(self.kana_frame, text="カタカナ優先", variable=self.kana_preference, value="katakana").pack(side=tk.LEFT)
        self.kana_frame.pack(side='left', padx=5)

        self.separator_entry_labelframe = tk.LabelFrame(self.row2_frame, text="符号文章内で符号を区切る任意の文字列")
        self.separator_entry = tk.Entry(self.separator_entry_labelframe)
        self.separator_entry.insert(0, "！！ ")
        self.separator_entry.pack(side=tk.LEFT)
        self.separator_entry_labelframe.pack(side='left', padx=5)

        # 二段目の配置フレームレイアウトマネージャー
        self.row2_frame.pack(pady=5)

        # 変換設定ラベルフレームのレイアウトマネージャー
        self.convert_settings_labelframe.pack(pady=5)

        # 変換の入力と出力
        self.convert_widget_labelframe = tk.LabelFrame(self, text="文章の入力と変換後の出力")
        self.input_frame = tk.Frame(self.convert_widget_labelframe)
        tk.Label(self.input_frame, text="文章の入力").pack()
        self.input_text = tk.Text(self.input_frame, height=10)
        self.input_text.pack()
        self.input_frame.pack()

        self.convert_button = tk.Button(self.convert_widget_labelframe, text="変換実行", command=self.convert)
        self.convert_button.pack()

        self.output_frame = tk.Frame(self.convert_widget_labelframe)
        tk.Label(self.output_frame, text="変換後の出力").pack()
        self.output_text = tk.Text(self.output_frame, height=10)
        self.output_text.pack()
        self.output_frame.pack()
        self.convert_widget_labelframe.pack(pady=5)

    def load_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.mapper = CodeMapper(path)
            messagebox.showinfo("読み込み完了", f"ファイルを読み込みました：{path}")

    def convert(self):
        if not self.mapper:
            messagebox.showwarning("未読み込み", "データセットファイルを読み込んでください")
            return

        input_str = self.input_text.get("1.0", tk.END).strip()
        sep = self.separator_entry.get()
        lang = self.lang_mode.get()
        code_type = self.code_type.get()
        direction = self.convert_mode.get()

        if lang == "JP":
            # colm7_JP_number_key, colm8_JP_upper_key, colm9_JP_lower_key, colm10_JP_overlapsymbol_key, colm11_JP_symbol_key, 
            # colm12_JP_hiragana_key, colm13_JP_katakana_key, colm14_JP_prosign_key
            base_cols = [
                "colm7_JP_number_key", "colm8_JP_upper_key", "colm9_JP_lower_key", "colm10_JP_overlapsymbol_key", "colm11_JP_symbol_key", "colm14_JP_prosign_key"
            ]
            kana_col = "colm12_JP_hiragana_key" if self.kana_preference.get() == "hiragana" else "colm13_JP_katakana_key"
            char_cols = base_cols + [kana_col]
        else:
            # colm1_US_number_key, colm2_US_upper_key, colm3_US_lower_key, colm4_US_symbol_key, colm5_US_prosign_key, colm6_US_overlap_flag
            char_cols = ["colm1_US_number_key", "colm2_US_upper_key", "colm3_US_lower_key", "colm4_US_symbol_key", "colm5_US_prosign_key"]

        code_col = "colm18_value_v7morlus" if code_type == "V7" else "colm16_value_standardmorlus"

        if direction == "to_code":
            mapping = self.mapper.build_mapping(lang, char_cols, code_col)
            output = self.to_code(input_str, mapping, sep)
        else:
            mapping = self.mapper.build_reverse_mapping(lang, char_cols, code_col)
            output = self.to_text(input_str, mapping, sep)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)

    def to_code(self, text, mapping, sep):
        result = []
        for ch in text:
            if ch in mapping:
                result.append(mapping[ch])
            else:
                result.append(ch)
        return sep.join(result)

    def to_text(self, text, mapping, sep):
        parts = text.split(sep)
        result = []
        for p in parts:
            if p in mapping:
                result.append(mapping[p])
            else:
                result.append(p)
        return "".join(result)


if __name__ == "__main__":
    app = Application()
    app.mainloop()

