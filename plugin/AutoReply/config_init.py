from utils.cfg_loader import *
import os

if not os.path.exists("./config/AutoReply"):
    os.mkdir("./config/AutoReply")

if not os.path.exists(r'./config/AutoReply/config.yml'):
    _cfg = dict(norepeat=False, norepeatgroup=[0], useAt=False, repeatconfig=dict(
        repeatQ=20, repeatmsg=1, interruptQ=0.5, interruptQQ=0.1, autoreply=True, kwreply=True))
    write_file(content=_cfg, path=r'./config/AutoReply/config.yml')

if not os.path.exists("./data/AutoReply"):
    os.mkdir("./data/AutoReply")
if not os.path.exists(r'./data/AutoReply/reply.yml'):
    _reply = [
        "对不起骗了大家，其实我没有考上浙大。。。\n对不起。列表的各位朋友，很抱歉，但是我觉得是时候向大家坦白了。\n本人去年七月参加高考，考前生活糜烂骄奢、声色犬马，最终落榜。\n但碍于面子，我很难开口向大家坦白我只考上了浙江某不知名的大学。\n所以我PS了浙江大学的录取通知，在网上搬运了浙江大学录取通知书的开箱视频。为了满足自己的虚荣心，并且不被大家发现，我在开学来到浙江后找的同学要到了大学校园卡，偶尔溜进学校，偷着拍几张照片，假装自己真的是浙大的学生。\n我以为我可以这样生活很久，直到今天晚上和同学出来鬼混，又从正门处看到了“求是创新”几个大字，突然间有点感慨，扪心自问，是否应该继续这样下去。\n还是选择向大家坦白吧，希望得到大家的原谅。见识了很漂亮的校园，认识了很多有趣的哥哥姐姐和同学，但以后应该不会再见面了吧，我要学会与自己和解感慨赋诗一首:\n今知不是此间人\n天意难解意难平\n风萧萧兮易水寒\n狂妄书生泪痕干\n星河载船满清梦\n期与游龙共徘徊\n似醒似梦飞花轻\n微雨明月弄清影\n我劝天公重抖擞\n五陵少年亦回头\n十年寒窗空自愁",
        "“疯子。”这是她给我发的最后一条消息，然后我就被删除，只剩下一个又一个红色感叹号。我到处借电话和微信联系她，但她置之不理，装作没有看到。我突然想起分手前就是这样，她看到消息不回，而我假意不知，若无其事地和她分享日常，偶尔她过意不去，就会随意地回我几句。我们就这样走了很久，没有争吵，没有指责，对外还是恩爱的小情侣。\n狂风暴雨前，往往会有一段很平静的时光，我和她大概就是这样。但事情的爆发比我预想中来得更快，我的朋友在烧烤店偶遇到她和一群人聚餐，她小鸟依人地靠在旁边的人身上。朋友把照片发给我的时候，我终于不能再继续自欺欺人下去，当作什么事情都没有发生。其实我一早就发现许多蛛丝马迹，比如她敷衍我时发的可爱表情包，比如她送给我的礼物明显就是男孩子的心思。\n“星辰万里，比不上千分之一的你。”她曾在七夕当天发过这样一条朋友圈，配图是某处的星空，评论都在感慨我们的神仙爱情，我也一度因此喜悦，但那天我们没见面，甚至连话都没有说几句。我下意识忽略掉这些，一心一意相信着我和她的感情。后来事情暴露，我顺藤摸瓜找到那个人的微博，有一张她俩七夕在星空下的合照，我恍然大悟。\n期盼的越多，往往失去的就越多。我一直在计划着我们的将来，关于学习，关于城市，关于家庭，而在每一个我因为未来辗转难眠的夜晚，她都在计划着离开我，都在奔赴旁人。我问好友，是不是我想要的太多，所以最后我连她都留不住。好友沉默好久才回我：“可你明明是受害者。”\n四月底的时候，我去了她的城市看她。考大学的时候，我们互相抄了对方的志愿，在志愿填报截止的前一刻我瞒着她改掉了志愿，最后我留在了本省的学校，而她去了外地。我瞒着她去的，可到了学校给她打电话，她支支吾吾半天才跟我说，她出去旅游了，和几个好朋友。同样是看那个男孩的微博我才知道，四月份的时候他们就已经厮混在一起。\n微博上的内容很多，从他们相遇到每一次的相处，我一个一个翻看，看他们的爱情。真讽刺啊，我们认识几年，比不上她和一个人的惊鸿一面。\n我恶心得想吐，疯狂发消息质问她，她起初还有些愧疚，后来直接恶言相向。我问她是不是不爱了，她冷漠的回了一句：“是。”\n五年，我们在一起五年，终于还是败给了异地。或许也不是因为异地，仅仅只是因为她生性如此。\n十年前，我们初遇，她还是个小女孩，却信誓旦旦说要陪伴我。十年后，我问她为什么不要我了，她说：“你把每一段的第一个字连起来看一下。”",
        "我也想吃KFC",
    ]
    write_file(content=_reply, path=r'./data/AutoReply/reply.yml')
