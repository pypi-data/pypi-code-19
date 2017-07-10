import xlrd

from soogang.exc import ResourceHeaderMissing

headers = {
    'category': [u'品种', u'品名'],
    'trademark': [u'牌号', u'材质'],
    'spec': [u'规格'],
    'steelwork': [u'产地', u'钢厂'],
    'price': [u'价格', u'报价', u'单价', u'挂牌价', u'过磅价', u'销售定价', u'销售价', u'含税价'],

    'warehouse': [u'仓库', u'提货仓库'],

    'weight': [u'重量', u'吨位', u'吨重', u'卷重', u'件重', u'数量', u'可销量', u'可用量', u'可供量', u'可卖重量', u'开单量'],
    'package_code': [u'捆包号', u'卷号', u'板卷号'],

    'contract_code': [u'合同号', u'资源号'],
    'comment': [u'备注', u'等级', u'卡号'],
}
required_fields = ['category', 'trademark', 'spec', 'steelwork', 'price']


def parse_resource(file_contents):
    workbook = xlrd.open_workbook(file_contents=file_contents)

    resources = []
    best_fit = []

    for sheet in workbook.sheets():
        column_map = {}
        priority_map = {}
        data_start = False

        for row in range(sheet.nrows):
            # 一行对应一个资源
            res = {}

            for col in range(sheet.ncols):
                v = str(sheet.cell(row, col).value).strip()
                if not v:
                    continue

                if not data_start:
                    for key, names in headers.items():
                        for name in names:
                            # 一个col可能有多个name，get优先级最高的name
                            if name in ''.join(v.split()):
                                # name对应优先级更高
                                if key not in priority_map or priority_map[key] > names.index(name):
                                    # 记录第几列对应的这个属性
                                    column_map[col] = key
                                    # 该属性在headers对应属性列表中优先级
                                    priority_map[key] = names.index(name)

                        if col in column_map:
                            break
                else:
                    # 已经过了表头，获取资源的数据
                    if col in column_map:
                        key = column_map[col]
                        res[key] = v

            if not data_start:
                values = column_map.values()
                data_start = True

                for required_field in required_fields:
                    if required_field not in values:
                        # 只有一行包括所有必须属性，才算合法的表头
                        data_start = False

                if not data_start:
                    current_fit = list(set(column_map.values()))
                    # best_fit 只是为了提供错误信息
                    if len(current_fit) > len(best_fit):
                        best_fit = current_fit

                    # reset 表头信息
                    column_map = {}
                    priority_map = {}

            else:
                # 资源数据类型化
                try:
                    res['price'] = float(res['price'])
                except (ValueError, KeyError):
                    res['price'] = 0

                try:
                    res['weight'] = float(res['weight'])
                except (ValueError, KeyError):
                    res['weight'] = 0

                # 下面4个属性为空，该行资源无效
                if 'category' not in res or not res['category']:
                    continue

                if 'trademark' not in res or not res['trademark']:
                    continue

                if 'steelwork' not in res or not res['steelwork']:
                    continue

                if 'spec' not in res or not res['spec']:
                    continue

                resources.append(res)

    if not resources:
        msg = u'无法解析资源单, 表头中缺少'

        for required_field in required_fields:
            if required_field not in best_fit:
                msg += '%s(%s)' % (headers[required_field][0], ','.join(headers[required_field][1:]))

        raise ResourceHeaderMissing(msg)

    ready_resources = []
    for res in resources:
        if res['category'] and res['trademark'] and res['steelwork'] and res['spec'] and res['price']:
            ready_resources.append(res)

    return ready_resources
