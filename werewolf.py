from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import asyncio
import random
from collections import Counter

# 游戏状态
game_state = {
    "mode": None,
    "players": [],
    "player_words": {},
    "undercover": None,
    "whiteboard": None,
    "word_pair": ("", ""),
    "status": "idle",
    "chat_id": None
}

Wolf = "https://i.imgur.com/VSpL0M6.jpeg"
WolfStart = "https://i.imgur.com/61vnCJc.jpeg"

# 示例词库
word_pairs = [
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),
    ("床", "沙发"),
    ("篮球", "足球"),
    ("炸鸡", "烤鸭"),
    ("飞机", "火车"),
    ("苹果", "香蕉"),
    ("猫", "老虎"),
    ("电脑", "电视"),
    ("冰箱", "空调"),
    ("洗衣机", "烘干机"),
    ("面包", "蛋糕"),
    ("剪刀", "刀子"),
    ("纸巾", "厕纸"),
    ("帽子", "头盔"),
    ("手表", "闹钟"),
    ("汉堡", "热狗"),
    ("口红", "润唇膏"),
    ("雨伞", "雨衣"),
    ("钱包", "卡包"),
    ("电动车", "自行车"),
    ("游泳", "冲浪"),
    ("椅子", "板凳"),
    ("眼镜", "墨镜"),
    ("电话", "手机"),
    ("袜子", "鞋垫"),
    ("耳机", "麦克风"),
    ("饮料", "果汁"),
    ("茶叶", "咖啡"),
    ("饺子", "包子"),
    ("裙子", "连衣裙"),
    ("漫画", "小说"),
    ("手电筒", "蜡烛"),
    ("啤酒", "白酒"),
    ("台灯", "吊灯"),
    ("浴巾", "毛巾"),
    ("奶茶", "咖啡"),
    ("公交车", "地铁"),
    ("书包", "背包"),
    ("草莓", "蓝莓"),
    ("洗发水", "沐浴露"),
    ("饼干", "蛋糕"),
    ("手套", "口罩"),
    ("照片", "画像"),
    ("火锅", "烧烤"),
    ("充电器", "电源线"),
    ("眼影", "腮红"),
    ("钢琴", "吉他"),
    ("海边", "沙滩"),
    ("医生", "护士"),
    ("老师", "讲师"),
    ("司机", "乘客"),

]

# 游戏入口：选择模式
async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        await query.message.delete()
    except:
        pass

    votes.clear()
    eliminated.clear()

    game_state.update({
        "players": [],
        "player_words": {},
        "undercover": None,
        "whiteboard": None,
        "word_pair": ("", ""),
        "status": "registering",
        "chat_id": query.message.chat_id
    })

    try:
        msg = await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=Wolf,
            caption="📢 🕵️‍♂️ 谁是卧底 游戏开始!\n请在 20 秒内点击下方按钮报名 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("我要参加", callback_data="werewolf:join")]
            ])
        )
        game_state["join_msg_id"] = msg.message_id
    except Exception as e:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"❗ 图片发送失败：{e}")
        return

    context.job_queue.run_once(end_registration, 20, data=query.message.chat_id)


# 玩家点击参加
async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    uname = query.from_user.full_name
    await query.answer("你已报名！", show_alert=True)
    if uid not in game_state["players"]:
        game_state["players"].append(uid)
        context.bot_data[uid] = {"name": uname}
    count = len(game_state["players"])
    text = f"📌 当前已报名人数：{count} 人"
    await context.bot.edit_message_caption(
        chat_id=query.message.chat_id,
        message_id=game_state.get("join_msg_id"),
        caption=text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("我要参加", callback_data="werewolf:join")]])
    )

# 查看词语按钮
async def view_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    word = game_state["player_words"].get(uid)
    if word is None:
        await query.answer("你不在游戏中。", show_alert=True)
    else:
        await query.answer(f"你的词语是：{'（空白）' if word == '' else word}", show_alert=True)

# 报名结束 → 发词
async def end_registration(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    bot = context.bot
    players = game_state["players"]


    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=game_state.get("join_msg_id")
        )
    except:
        pass


    if len(players) < 2:
        await bot.send_message(chat_id, "❌ 人数不足，游戏取消。")
        game_state["status"] = "idle"
        return

    pair = random.choice(word_pairs)
    game_state["word_pair"] = pair
    random.shuffle(players)
    game_state["undercover"] = players[-1]
    if len(players) >= 7:
        game_state["whiteboard"] = players[-2]

    for uid in players:
        if uid == game_state["undercover"]:
            game_state["player_words"][uid] = pair[1]
        elif uid == game_state["whiteboard"]:
            game_state["player_words"][uid] = ""
        else:
            game_state["player_words"][uid] = pair[0]

    names = [context.bot_data.get(uid, {}).get("name", f"玩家({uid})") for uid in players]
    players_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(names)])
    await bot.send_message(chat_id, f"✅ 报名结束，当前玩家名单：\n{players_list}")

    await asyncio.sleep(3)
    btn = [[InlineKeyboardButton("点击查看我的词语", callback_data="werewolf:view")]]
    await bot.send_photo(chat_id,photo=WolfStart,caption= "🎮 游戏开始！请点击下方按钮查看你的词语 👇", reply_markup=InlineKeyboardMarkup(btn))
    await start_description_phase(chat_id, context)

# 描述阶段
async def start_description_phase(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    players = game_state["players"]
    await asyncio.sleep(5)
    await bot.send_message(chat_id, "🗣 描述阶段开始！请每位玩家按照顺序描述你的词语。\n\n⚠️ 请真实描述，不可说谎。倒计时30秒")

    context.job_queue.run_once(start_vote_phase, 30, data=chat_id)


# 导出函数供 bot.py 使用
__all__ = [
    "set_mode",
    "join_game",
    "view_word",
    "end_registration",
    "start_description_phase",
    "start_vote_phase",
    "handle_vote",
    "handle_vote2",
    "start_game_restart",
    "reveal_result",
    "game_state"
]

# 投票记录
votes = {}            # uid: voted_uid
eliminated = set()    # 被淘汰玩家

# 启动投票阶段
async def start_vote_phase(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    bot = context.bot
    votes.clear()
    
    keyboard = []
    for uid in game_state["players"]:
        if uid in eliminated:
            continue
        uname = context.bot_data.get(uid, {}).get("name", str(uid))
        keyboard.append([InlineKeyboardButton(uname, callback_data=f"werewolf:vote:{uid}")])

    msg = await bot.send_message(
        chat_id,
        "📤 投票时间到！请选择你认为是卧底的玩家 👇\n\n请点击以下玩家名字投票：",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context._chat_data[chat_id]["vote_msg_id"] = msg.message_id

# 接收投票操作
async def handle_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    voter = query.from_user.id
    voted_uid = int(query.data.split(":")[-1])

    if voter not in game_state["players"] or voter in eliminated:
        await query.answer("你已被淘汰，无法投票！", show_alert=True)
        return
    if voter in votes:
        await query.answer("你已投过票了！", show_alert=True)
        return

    votes[voter] = voted_uid
    await query.answer("✅ 投票成功！", show_alert=True)

    # 所有人投完就统计结果
    active_voters = [uid for uid in game_state["players"] if uid not in eliminated]
    if len(votes) == len(active_voters):
        await count_votes_and_check(query.message.chat_id, context)

# 投票结果统计 + 胜负判断
async def count_votes_and_check(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot

    # 统计票数
    count = {}
    for uid in votes.values():
        count[uid] = count.get(uid, 0) + 1

    try:
        await context.bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=context._chat_data[chat_id].get("vote_msg_id"),  # 确保你保存过按钮的 message_id
            reply_markup=None
        )
    except:
        pass



    max_votes = max(count.values())
    top = [uid for uid, v in count.items() if v == max_votes]

    if len(top) > 1:
        names = []
        for uid in top:
            uname = context.bot_data.get(uid, {}).get("name", str(uid))
            names.append(f"<a href='tg://user?id={uid}'>{uname}</a>")
        name_text = "、".join(names)

        await bot.send_message(
            chat_id,
            f"⚠️ 出现平票情况！\n请 {name_text} 发言~\n🕒 发言时间：20 秒",
            parse_mode=ParseMode.HTML
        )

        await asyncio.sleep(20)
        await second_round(chat_id, context, top)
        return


    # 淘汰玩家
    eliminated_uid = top[0]
    game_state["eliminated"].add(eliminated_uid)

    # 判断是否为游戏结束
    is_undercover = eliminated_uid == game_state["undercover"]
    is_whiteboard = eliminated_uid == game_state.get("whiteboard")
    whiteboard_exists = game_state.get("whiteboard") is not None

    # 游戏结束逻辑判断
    if is_undercover and not (whiteboard_exists and not is_whiteboard):
        # 卧底出局，白板已无影响（或没有白板）
        await announce_elimination(eliminated_uid, chat_id, context, is_game_end=True)
        return
    elif is_whiteboard and not (whiteboard_exists and not is_undercover):
        # 白板出局，卧底已无影响（或没有卧底）
        await announce_elimination(eliminated_uid, chat_id, context, is_game_end=True)
        return
    else:
        # 游戏继续
        await announce_elimination(eliminated_uid, chat_id, context, is_game_end=False)


# 第二轮描述 + 投票（平票处理）
async def second_round(chat_id: int, context: ContextTypes.DEFAULT_TYPE, tied_players: list):
    bot = context.bot
  
    # 二轮投票
    global votes
    votes.clear()
    keyboard = []
    for uid in tied_players:
        uname = context.bot_data.get(uid, {}).get("name", str(uid))
        keyboard.append([InlineKeyboardButton(uname, callback_data=f"werewolf:vote2:{uid}")])
    await bot.send_message(chat_id, "🔁 第二轮投票开始！", reply_markup=InlineKeyboardMarkup(keyboard))

# 第二轮投票逻辑
async def handle_vote2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    voter_name = context.bot_data.get(uid, {}).get("name", str(uid))
    chat_id = query.message.chat.id

    # ✅ 防重复投票
    if uid in votes:
        await query.answer("你已经投过票了", show_alert=True)
        return

    # ✅ 记录投票
    voted_uid = int(query.data.split(":")[-1])
    votes[uid] = voted_uid

    await query.answer()
    await context.bot.send_message(chat_id, f"📩 {voter_name} 已投票")

    # ✅ 检查是否所有存活玩家都投完票
    active_players = [uid for uid in game_state["players"] if uid not in eliminated]
    if len(votes) < len(active_players):
        return  # 等待其他人投票

    # ✅ 所有人已投票，开始统计
    vote_counts = Counter(votes.values())
    max_votes = max(vote_counts.values())
    top = [uid for uid, count in vote_counts.items() if count == max_votes]

    await context.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=query.message.message_id,
        reply_markup=None
    )


    # ✅ 第二轮再次平票 → 全体平票者淘汰
    if len(top) > 1:
        for uid in top:
        eliminated.add(uid)

    await context.bot.send_message(chat_id, f"📛 第二轮仍平票，平票玩家全部淘汰！")

    # 判断是否包含卧底并决定游戏是否结束
    if game_state["undercover"] in top:
        await announce_elimination(None, chat_id, context, is_game_end=True)
    else:
        await announce_elimination(None, chat_id, context, is_game_end=True)
    return  

    # ✅ 正常淘汰票数最高的一人
    target = top[0]
    eliminated.add(target)
    await announce_elimination(target, chat_id, context)
    return



# 公布身份与重启按钮
async def reveal_result(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    msg = (
        f"🎯 本局词语：\n"
        f"▪️ 平民词：{game_state['word_pair'][0]}\n"
        f"▪️ 卧底词：{game_state['word_pair'][1]}\n\n"
        f"👥 玩家身份：\n"
    )

    for uid in game_state["players"]:
        role = "卧底" if uid == game_state["undercover"] else "白板" if uid == game_state["whiteboard"] else "平民"
        name = context.bot_data.get(uid, {}).get("name", str(uid))
        msg += f"- {name}：{role}\n"

    await bot.send_message(chat_id, msg, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 重新开始", callback_data="werewolf:restart")],
        [InlineKeyboardButton("🎮 切换游戏模式", callback_data="mainmenu")]
    ]))


async def announce_elimination(uid, chat_id, context: ContextTypes.DEFAULT_TYPE, is_game_end=False):
    uname = context.bot_data.get(uid, {}).get("name", str(uid))
    mention = f"<a href='tg://user?id={uid}'>{uname}</a>"
    if is_game_end:
        await context.bot.send_message(chat_id, f"{mention} 淘汰！卧底被抓到了！", parse_mode=ParseMode.HTML)
        await reveal_result(chat_id, context)
    else:
        await context.bot.send_message(chat_id, f"{mention} 淘汰！游戏继续！", parse_mode=ParseMode.HTML)


async def start_game_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    await query.message.edit_reply_markup(reply_markup=None)


    # 重置数据
    game_state.update({
        "players": [],
        "player_words": {},
        "undercover": None,
        "whiteboard": None,
        "word_pair": ("", ""),
        "status": "registering",
        "chat_id": chat_id
    })
    eliminated.clear()
    votes.clear()

    keyboard = [[InlineKeyboardButton("我要参加", callback_data="werewolf:join")]]
    await context.bot.send_message(
        chat_id=chat_id,
        text="新一轮《谁是卧底》开始报名啦！请点击下方按钮加入 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.job_queue.run_once(end_registration, 20, data=chat_id)

