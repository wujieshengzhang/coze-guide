"""
Coze国内版基于IDE开发插件，开发moonshot模型的token计算器
"""

from runtime import Args
from typings.TokenCalculation.TokenCalculation import Input, Output
import requests

"""
Each file needs to export a function named `handler`. This function is the entrance to the Tool.

Parameters:
args: parameters of the entry function.
args.input - input parameters, you can get test input value by args.input.xxx.
args.logger - logger instance used to print logs, injected by runtime.

Remember to fill in input/output in Metadata, it helps LLM to recognize and use tool.

Return:
The return data of the function, which should match the declared output parameters.
"""


def handler(args: Args[Input]) -> Output:
    api_key = args.input.api_key
    content = args.input.content
    model = args.input.model

    # 如果模型未定义，设置默认值
    if not model:
        model = "moonshot-v1-8k"

    # 计算 token 的 url
    url = "https://api.moonshot.cn/v1/tokenizers/estimate-token-count"

    # 设置 header
    header = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {api_key}".format(api_key=api_key)
    }

    # 设置 body
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }

    # 发起 http 请求
    res = requests.post(url=url, json=data, headers=header)

    # res 返回值可能不为 json，加一个异常处理
    try:
        res_text = res.json()
        # 如果 error 不在 res_text 的 key 中，则可以认为成功，返回token数
        # ref: https://platform.moonshot.cn/docs/api/misc#%E8%BF%94%E5%9B%9E%E5%86%85%E5%AE%B9
        if "error" not in res_text.keys():
            result = {
                "total_tokens": res_text["data"]["total_tokens"],
                "code": res_text["code"],
                "status": res_text["status"]
            }
        else:
            # 如果出现 error，返回异常信息
            result = {
                "code": res_text["code"],
                "error": res_text["error"],
                "message": res_text["message"],
                "status": res_text["message"]
            }

    except:
        # 如果出现异常，返回 -1
        result = {
            "total_tokens": -1,
            "code": -1,
            "status": False
        }

    return result


