from collections import namedtuple

Column = namedtuple('Column',
                    ['name', 'attr_name', 'max_width', 'fixed_width', 'filter'])


class TableFormatter:
    def __init__(self):
        self.columns = {}
        self.rows = []
        self.column_margin = 2
        self.with_header = True

        self.inited = False
        self.col_sizes = None
        self.header = ""

    def add_column(self, column_name, attr_name,
                   max_width=None, fixed_width=None, filter=None):
        self.columns[attr_name] = Column(column_name, attr_name,
                                         max_width, fixed_width, filter)
        return self

    def add_rows(self, rows):
        self.rows += rows

    def clear_rows(self):
        self.rows = []

    def init(self):
        self.col_sizes = self.calculate_column_size(self.with_header)
        self.inited = True

    def print_header(self):
        if not self.inited:
            self.init()
        header = self.format_row({k: t.name for k, t in self.columns.items()}, True)
        header = header[:-3]

        self.header = header
        print(header)
        print("-" * len(header))

    def print_formatted(self):
        if self.with_header:
            self.print_header()

        # format rows
        for row in self.rows:
            print(self.format_row(row), end="")

        if self.with_header:
            print("=" * len(self.header))

    def format_row(self, row, header=False):
        if not self.inited:
            self.init()
        formatted = ""
        formatted_cols = []
        for name, col in self.columns.items():
            item = self.get_item(row, name)
            if col.filter and not header:
                item = col.filter(item)

            formatted_cols.append([
                self.col_sizes[name],
                self.pad_or_wrap(item, self.col_sizes[name])
            ])

        i = 0
        buffer = ""
        while True:
            missed = 0
            for formatted_col in formatted_cols:
                if i < len(formatted_col[1]):
                    buffer += formatted_col[1][i]
                else:
                    missed += 1
                    buffer += formatted_col[0] * " "
                buffer += self.column_margin * " "
            if missed == len(formatted_cols):
                break
            else:
                formatted += buffer + "\n"
                buffer = ""
            i += 1

        return formatted

    def calculate_column_size(self, with_header=True):
        column_sizes = {}
        for name, col in self.columns.items():
            if col.fixed_width is not None:
                column_sizes[name] = col.fixed_width
                continue

            rows = map(lambda row: self.get_item(row, name), self.rows)
            if col.filter:
                rows = [col.filter(row) for row in rows]

            col_len = self.find_max_len(rows)
            if with_header:
                col_len = max(len(self.columns[name].name), col_len)

            if not col.max_width or col_len <= col.max_width:
                column_sizes[name] = col_len
            else:
                column_sizes[name] = col.max_width
        return column_sizes

    @staticmethod
    def get_item(row, name):
        if isinstance(row, dict):
            item = row[name]
        else:
            item = getattr(row, name)

        return item

    @staticmethod
    def find_max_len(items):
        max_len = 0
        for item in items:
            len_ = len(item)
            if len_ > max_len:
                max_len = len_
        return max_len

    @classmethod
    def pad_or_wrap(cls, item, length):
        item_len = len(item)
        if item_len <= length:
            item += " " * (length - item_len)
            return [item]
        elif item_len > length:
            items = cls.wrap(item, length).split("\n")
            return items

    @staticmethod
    def wrap(_str, max_length=79, ignore_linebreak=False):
        breaker = [" ", ",", ".", "-", ";", ":", "\n"]

        result = ""
        buf = ""
        line_len = 0
        i = 0
        _str += " "
        total_len = len(_str)

        while i < total_len:
            s = _str[i]
            if s == "\n":
                if ignore_linebreak:
                    s = " "
                else:
                    result += buf + "\n"
                    line_len = 0
                    buf = ""
                    i += 1
                    continue

            buf += s

            if s in breaker or i == total_len - 1:
                if line_len + len(buf) > max_length:
                    result += "\n" if result else ""
                    line_len = 0
                    if len(buf) <= max_length:
                        result += buf
                        line_len = len(buf)
                    else:
                        buf_pos = 0
                        while buf_pos < len(buf):
                            if line_len < max_length - 2:
                                result += buf[buf_pos]
                                line_len += 1
                            else:
                                if buf_pos == len(buf) - 1:
                                    result += buf[buf_pos] + "\n"
                                    buf_pos += 1
                                    line_len = 0
                                elif buf[buf_pos + 1] in breaker:
                                    result += buf[buf_pos] + buf[buf_pos + 1] \
                                        + "\n"
                                    buf_pos += 1
                                    line_len = 0
                                else:
                                    result += buf[buf_pos] + "-\n"
                                    line_len = 0
                            buf_pos += 1
                    buf = ""
                else:
                    result += buf
                    line_len += len(buf)
                    buf = ""

            i += 1

        return result.rstrip()
