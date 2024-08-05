import panel as pn
import param
import openai
from db import DB
from chain import Chain
from utils import get_openai_key

# set openai key
openai.api_key = get_openai_key()

# 定义界面的小部件
file_input = pn.widgets.FileInput(accept='.pdf')  # PDF 文件的文件输入小部件
button_load = pn.widgets.Button(name="Load DB", button_type='primary')  # 加载数据库的按钮
input_box = pn.widgets.TextInput(placeholder='Enter text here…')  # 用于用户查询的文本输入小部件


# 用于存储聊天记录、回答、数据库查询和回复
class Chatbot(param.Parameterized):
    # save chat history will combine with user query send to qa chain
    chat_history = param.List([])
    # save llm result answer
    answer = param.String("")
    # save query for db
    db_query = param.String("")
    # save db top k related response docs
    db_response = param.List([])

    def __init__(self, file, llm_name, chain_type, k, **params):
        super().__init__(**params)
        # attributes
        self.panels = []
        self.file = file
        self.llm_name = llm_name
        self.chain_type = chain_type
        self.k = k

        self.qa = self.generate_qa(file=file)

    def generate_qa(self, file):
        # initial vector db
        db = DB(file=file)
        # load pdf reader vector db
        pdf_db = db.pdf_load_db()
        # initial chain
        chain = Chain(llm_name=self.llm_name, db=pdf_db)
        # build conversational qa chain
        qa = chain.build_chain(chain_type=self.chain_type, k=self.k)

        return qa

    # 将文档加载到聊天机器人中
    def call_load_db(self, count):
        """
        count: 数量
        """
        if count == 0 or file_input.value is None:  # 初始化或未指定文件
            return pn.pane.Markdown(f"Loaded File: {self.file}")
        else:
            file_input.save("temp.pdf")  # 本地副本
            self.file = f"./docs/pdf_test/{file_input.filename}"
            button_load.button_style = "outline"
            self.qa = self.generate_qa(file=self.file)
            button_load.button_style = "solid"

        self.clr_history()
        return pn.pane.Markdown(f"Loaded File: {self.file}")

    # 处理对话链
    def conv_chain(self, query):
        """
        query: 用户的查询
        """
        if not query:
            return pn.WidgetBox(pn.Row('User:', pn.pane.Markdown("", width=600)), scroll=True)
        result = self.qa({"question": query, "chat_history": self.chat_history})
        self.chat_history.extend([(query, result["answer"])])
        self.db_query = result["generated_question"]
        self.db_response = result["source_documents"]
        self.answer = result['answer']
        self.panels.extend([
            pn.Row('User:', pn.pane.Markdown(query, width=600)),
            pn.Row('ChatBot:', pn.pane.Markdown(self.answer, width=600, styles={'background-color': '#F6F6F6'}))
        ])
        input_box.value = ''  # 清除时清除装载指示器
        return pn.WidgetBox(*self.panels, scroll=True)

    # 获取最后发送到数据库的问题
    @param.depends('db_query ', )
    def get_last_question(self):
        if not self.db_query:
            return pn.Column(
                pn.Row(pn.pane.Markdown(f"Last question to DB:", styles={'background-color': '#F6F6F6'})),
                pn.Row(pn.pane.Str("no DB accesses so far"))
            )
        return pn.Column(
            pn.Row(pn.pane.Markdown(f"DB query:", styles={'background-color': '#F6F6F6'})),
            pn.pane.Str(self.db_query)
        )

    # 获取数据库返回的源文件
    @param.depends('db_response', )
    def get_sources(self):
        if not self.db_response:
            return
        rlist = [pn.Row(pn.pane.Markdown(f"Result of DB lookup:", styles={'background-color': '#F6F6F6'}))]
        for doc in self.db_response:
            rlist.append(pn.Row(pn.pane.Str(doc)))
        return pn.WidgetBox(*rlist, width=600, scroll=True)

    # 获取当前聊天记录
    @param.depends('conv_chain', 'clr_history')
    def get_chats(self):
        if not self.chat_history:
            return pn.WidgetBox(pn.Row(pn.pane.Str("No History Yet")), width=600, scroll=True)
        rlist = [pn.Row(pn.pane.Markdown(f"Current Chat History variable", styles={'background-color': '#F6F6F6'}))]
        for exchange in self.chat_history:
            rlist.append(pn.Row(pn.pane.Str(exchange)))
        return pn.WidgetBox(*rlist, width=600, scroll=True)

    # 清除聊天记录
    def clr_history(self):
        self.chat_history = []
        return


file = './docs/matplotlib/第一回：Matplotlib初相识.pdf'
llm_name = 'gpt-3.5-turbo'
chain_type = 'stuff'
k = 4
chatbot = Chatbot(file, llm_name, chain_type, k)
button_clear_history = pn.widgets.Button(name="Clear History", button_type='warning')  # 清除聊天记录的按钮
button_clear_history.on_click(chatbot.clr_history)  # 将清除历史记录功能绑定到按钮上

# 将加载数据库和对话的函数绑定到相应的部件上
bound_button_load = pn.bind(chatbot.call_load_db, button_load.param.clicks)
conversation = pn.bind(chatbot.conv_chain, input_box)

jpg_pane = pn.pane.Image('./img/convchain.jpg')

# 使用 Panel 定义界面布局
tab1 = pn.Column(
    pn.Row(input_box),
    pn.layout.Divider(),
    pn.panel(conversation, loading_indicator=True, height=300),
    pn.layout.Divider(),
)
tab2 = pn.Column(
    pn.panel(chatbot.get_last_question),
    pn.layout.Divider(),
    pn.panel(chatbot.get_sources),
)
tab3 = pn.Column(
    pn.panel(chatbot.get_chats),
    pn.layout.Divider(),
)
tab4 = pn.Column(
    pn.Row(file_input, button_load, bound_button_load),
    pn.Row(button_clear_history, pn.pane.Markdown("Clears chat history. Can use to start a new topic")),
    pn.layout.Divider(),
    pn.Row(jpg_pane.clone(width=400))
)
# 将所有选项卡合并为一个仪表盘
dashboard = pn.Column(
    pn.Row(pn.pane.Markdown('# ChatWithYourData_Bot')),
    pn.Tabs(('Conversation', tab1), ('Database', tab2), ('Chat History', tab3), ('Configure', tab4))
)

# run chatbot
dashboard.servable()
