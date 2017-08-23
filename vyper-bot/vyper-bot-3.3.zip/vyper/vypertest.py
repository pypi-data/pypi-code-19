import pluginbot
import keyboard
class VyperBot(pluginbot.PluginBot):
	def message(self, msg):
		msg = msg['message']
		print(msg)
		self.test_plugins(msg)

	def callback_query(self, msg):
		print(msg)

class Keyboard(pluginbot.Plugin):
	def execute(self, msg):
		print('Testing keyboard')
		if msg['text'] == "/kb":
			print('Keyboard')
			kb = keyboard.Keyboard()
			kb.load_from_excel('keyboard.xls')
			self.bot.sendMessage(msg['chat']['id'], 'Inline keyboard test', reply_markup=kb.json)
if __name__ == "__main__":
	bot = VyperBot('402125473:AAEewgo3teZvpPc23gThnA0nVKqTPYuXq_0', start_loop=True, list_plugins=True)
	