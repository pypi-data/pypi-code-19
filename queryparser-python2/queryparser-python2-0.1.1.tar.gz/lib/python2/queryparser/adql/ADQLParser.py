# Generated from src/queryparser/adql/ADQLParser.g4 by ANTLR 4.7
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3")
        buf.write(u"\u0132\u04a2\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6")
        buf.write(u"\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4")
        buf.write(u"\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t")
        buf.write(u"\22\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27")
        buf.write(u"\4\30\t\30\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4")
        buf.write(u"\35\t\35\4\36\t\36\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t")
        buf.write(u"#\4$\t$\4%\t%\4&\t&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4")
        buf.write(u",\t,\4-\t-\4.\t.\4/\t/\4\60\t\60\4\61\t\61\4\62\t\62")
        buf.write(u"\4\63\t\63\4\64\t\64\4\65\t\65\4\66\t\66\4\67\t\67\4")
        buf.write(u"8\t8\49\t9\4:\t:\4;\t;\4<\t<\4=\t=\4>\t>\4?\t?\4@\t@")
        buf.write(u"\4A\tA\4B\tB\4C\tC\4D\tD\4E\tE\4F\tF\4G\tG\4H\tH\4I\t")
        buf.write(u"I\4J\tJ\4K\tK\4L\tL\4M\tM\4N\tN\4O\tO\4P\tP\4Q\tQ\4R")
        buf.write(u"\tR\4S\tS\4T\tT\4U\tU\4V\tV\4W\tW\4X\tX\4Y\tY\4Z\tZ\4")
        buf.write(u"[\t[\4\\\t\\\4]\t]\4^\t^\4_\t_\4`\t`\4a\ta\4b\tb\4c\t")
        buf.write(u"c\4d\td\4e\te\4f\tf\4g\tg\4h\th\4i\ti\4j\tj\4k\tk\4l")
        buf.write(u"\tl\4m\tm\4n\tn\4o\to\4p\tp\4q\tq\4r\tr\4s\ts\4t\tt\4")
        buf.write(u"u\tu\4v\tv\4w\tw\4x\tx\4y\ty\4z\tz\4{\t{\4|\t|\4}\t}")
        buf.write(u"\4~\t~\4\177\t\177\4\u0080\t\u0080\4\u0081\t\u0081\3")
        buf.write(u"\2\3\2\3\3\3\3\3\3\3\3\3\3\3\4\5\4\u010b\n\4\3\4\3\4")
        buf.write(u"\3\5\3\5\5\5\u0111\n\5\3\5\3\5\3\5\3\5\3\5\3\6\3\6\3")
        buf.write(u"\7\3\7\3\b\3\b\3\t\3\t\3\n\5\n\u0121\n\n\3\n\3\n\3\13")
        buf.write(u"\3\13\3\f\3\f\3\f\3\f\3\f\3\f\5\f\u012d\n\f\3\r\3\r\3")
        buf.write(u"\r\3\r\3\r\3\r\7\r\u0135\n\r\f\r\16\r\u0138\13\r\3\16")
        buf.write(u"\3\16\5\16\u013c\n\16\3\17\3\17\3\17\3\17\3\17\3\17\3")
        buf.write(u"\17\3\17\3\17\3\17\3\17\3\20\3\20\3\21\3\21\3\21\3\21")
        buf.write(u"\3\21\3\22\3\22\7\22\u0152\n\22\f\22\16\22\u0155\13\22")
        buf.write(u"\3\22\3\22\3\23\3\23\3\23\5\23\u015c\n\23\3\23\3\23\3")
        buf.write(u"\23\3\23\5\23\u0162\n\23\7\23\u0164\n\23\f\23\16\23\u0167")
        buf.write(u"\13\23\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3")
        buf.write(u"\25\3\25\3\26\3\26\3\26\7\26\u0177\n\26\f\26\16\26\u017a")
        buf.write(u"\13\26\3\27\3\27\3\27\5\27\u017f\n\27\3\27\3\27\3\30")
        buf.write(u"\3\30\3\31\3\31\3\31\3\31\3\32\3\32\3\33\3\33\3\33\3")
        buf.write(u"\33\3\33\3\33\3\33\3\34\3\34\3\35\3\35\5\35\u0196\n\35")
        buf.write(u"\3\36\3\36\3\36\3\36\3\36\3\37\3\37\3\37\3\37\3\37\3")
        buf.write(u" \3 \3!\3!\3\"\3\"\3\"\3\"\3#\3#\3$\5$\u01ad\n$\3$\3")
        buf.write(u"$\3%\3%\3%\3%\3&\3&\5&\u01b7\n&\3\'\3\'\3(\3(\3(\3(\3")
        buf.write(u"(\3(\3(\3(\3(\3(\3(\3(\3(\3(\5(\u01c9\n(\3(\3(\3)\3)")
        buf.write(u"\3)\5)\u01d0\n)\5)\u01d2\n)\3)\3)\5)\u01d6\n)\3*\3*\3")
        buf.write(u"*\3+\3+\3+\3+\3+\3,\5,\u01e1\n,\3,\3,\3-\3-\3-\3-\7-")
        buf.write(u"\u01e9\n-\f-\16-\u01ec\13-\3.\3.\3/\3/\3/\5/\u01f3\n")
        buf.write(u"/\3/\3/\3/\3\60\3\60\3\60\3\60\3\60\3\60\3\60\5\60\u01ff")
        buf.write(u"\n\60\3\61\3\61\3\61\3\61\3\62\3\62\3\63\3\63\3\63\7")
        buf.write(u"\63\u020a\n\63\f\63\16\63\u020d\13\63\3\64\3\64\3\64")
        buf.write(u"\3\65\3\65\5\65\u0214\n\65\3\66\3\66\5\66\u0218\n\66")
        buf.write(u"\3\66\3\66\3\66\3\67\3\67\3\67\3\67\3\67\5\67\u0222\n")
        buf.write(u"\67\38\38\38\68\u0227\n8\r8\168\u0228\39\39\39\39\39")
        buf.write(u"\39\39\3:\3:\3;\3;\3;\3<\3<\5<\u0239\n<\3=\3=\3=\5=\u023e")
        buf.write(u"\n=\5=\u0240\n=\3>\3>\5>\u0244\n>\3>\5>\u0247\n>\3>\3")
        buf.write(u">\3>\5>\u024c\n>\3>\3>\3>\3>\5>\u0252\n>\3?\3?\5?\u0256")
        buf.write(u"\n?\3?\3?\3?\3?\3?\5?\u025d\n?\3?\3?\3?\5?\u0262\n?\3")
        buf.write(u"@\3@\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A")
        buf.write(u"\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3")
        buf.write(u"A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A")
        buf.write(u"\3A\3A\3A\3A\3A\3A\3A\3A\3A\5A\u02a2\nA\3A\3A\3A\3A\3")
        buf.write(u"A\3A\3A\3A\3A\3A\3A\5A\u02af\nA\3A\3A\5A\u02b3\nA\3B")
        buf.write(u"\3B\3B\3B\3B\3C\3C\3C\3C\5C\u02be\nC\3C\3C\3C\3C\3C\5")
        buf.write(u"C\u02c5\nC\3C\3C\5C\u02c9\nC\3D\3D\3D\3D\3D\5D\u02d0")
        buf.write(u"\nD\3E\3E\3E\3E\5E\u02d6\nE\3E\3E\5E\u02da\nE\3F\3F\3")
        buf.write(u"F\3F\5F\u02e0\nF\3G\3G\3G\5G\u02e5\nG\3G\3G\3H\3H\5H")
        buf.write(u"\u02eb\nH\3I\5I\u02ee\nI\3I\3I\5I\u02f2\nI\3J\3J\3J\3")
        buf.write(u"J\3J\5J\u02f9\nJ\3J\3J\3J\3J\3J\3J\3J\3J\3J\3J\3J\3J")
        buf.write(u"\3J\3J\3J\3J\3J\3J\7J\u030d\nJ\fJ\16J\u0310\13J\3K\3")
        buf.write(u"K\3K\3K\5K\u0316\nK\3L\3L\3L\3M\3M\3M\3M\3N\3N\3O\3O")
        buf.write(u"\3P\3P\3Q\3Q\3Q\3Q\3Q\3Q\3Q\3R\3R\3R\3R\3R\3R\3R\3R\3")
        buf.write(u"R\6R\u0335\nR\rR\16R\u0336\3R\3R\3S\3S\3S\3S\3S\3S\5")
        buf.write(u"S\u0341\nS\3T\3T\5T\u0345\nT\3U\3U\3U\5U\u034a\nU\3V")
        buf.write(u"\3V\3V\5V\u034f\nV\3V\3V\3V\5V\u0354\nV\3V\3V\3V\3V\5")
        buf.write(u"V\u035a\nV\3V\7V\u035d\nV\fV\16V\u0360\13V\3W\3W\3X\3")
        buf.write(u"X\5X\u0366\nX\3X\3X\3X\3Y\3Y\3Y\5Y\u036e\nY\3Y\3Y\3Y")
        buf.write(u"\5Y\u0373\nY\3Y\7Y\u0376\nY\fY\16Y\u0379\13Y\3Z\3Z\3")
        buf.write(u"[\3[\3[\3[\3[\3\\\3\\\3]\3]\3^\3^\3^\3^\3^\3^\7^\u038c")
        buf.write(u"\n^\f^\16^\u038f\13^\3_\3_\3_\3_\7_\u0395\n_\f_\16_\u0398")
        buf.write(u"\13_\5_\u039a\n_\3`\3`\5`\u039e\n`\3`\5`\u03a1\n`\3`")
        buf.write(u"\3`\3`\3a\3a\3a\3a\3a\5a\u03ab\na\3b\3b\3b\3b\3b\5b\u03b2")
        buf.write(u"\nb\3c\3c\3d\3d\3d\3e\3e\3f\3f\3g\5g\u03be\ng\3g\3g\3")
        buf.write(u"h\3h\5h\u03c4\nh\3i\3i\5i\u03c8\ni\3j\3j\3j\7j\u03cd")
        buf.write(u"\nj\fj\16j\u03d0\13j\3k\3k\3l\3l\3m\3m\5m\u03d8\nm\3")
        buf.write(u"n\3n\3n\3n\3o\3o\5o\u03e0\no\3o\5o\u03e3\no\3o\5o\u03e6")
        buf.write(u"\no\3o\5o\u03e9\no\3o\5o\u03ec\no\3p\3p\3p\5p\u03f1\n")
        buf.write(u"p\3p\3p\3q\3q\3q\5q\u03f8\nq\3q\3q\3q\3q\3q\3q\3q\5q")
        buf.write(u"\u0401\nq\3q\3q\5q\u0405\nq\3q\5q\u0408\nq\3q\3q\3q\5")
        buf.write(u"q\u040d\nq\7q\u040f\nq\fq\16q\u0412\13q\3r\3r\3s\3s\3")
        buf.write(u"s\3s\3s\3s\3s\3s\3s\3s\3s\3s\7s\u0422\ns\fs\16s\u0425")
        buf.write(u"\13s\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t")
        buf.write(u"\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3")
        buf.write(u"t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\3t\5t\u0456\nt")
        buf.write(u"\3u\3u\3v\3v\3w\3w\3x\3x\5x\u0460\nx\3y\3y\3y\5y\u0465")
        buf.write(u"\ny\3z\3z\3{\3{\3{\3{\3{\7{\u046e\n{\f{\16{\u0471\13")
        buf.write(u"{\5{\u0473\n{\3{\3{\3|\3|\3}\3}\3~\3~\3~\3~\5~\u047f")
        buf.write(u"\n~\3\177\3\177\3\177\3\177\3\177\3\177\3\177\5\177\u0488")
        buf.write(u"\n\177\3\u0080\3\u0080\3\u0080\3\u0081\3\u0081\3\u0081")
        buf.write(u"\3\u0081\3\u0081\7\u0081\u0492\n\u0081\f\u0081\16\u0081")
        buf.write(u"\u0495\13\u0081\3\u0081\3\u0081\5\u0081\u0499\n\u0081")
        buf.write(u"\3\u0081\3\u0081\3\u0081\5\u0081\u049e\n\u0081\3\u0081")
        buf.write(u"\3\u0081\3\u0081\2\n\30$\u0092\u00aa\u00b0\u00ba\u00e0")
        buf.write(u"\u00e4\u0082\2\4\6\b\n\f\16\20\22\24\26\30\32\34\36 ")
        buf.write(u"\"$&(*,.\60\62\64\668:<>@BDFHJLNPRTVXZ\\^`bdfhjlnprt")
        buf.write(u"vxz|~\u0080\u0082\u0084\u0086\u0088\u008a\u008c\u008e")
        buf.write(u"\u0090\u0092\u0094\u0096\u0098\u009a\u009c\u009e\u00a0")
        buf.write(u"\u00a2\u00a4\u00a6\u00a8\u00aa\u00ac\u00ae\u00b0\u00b2")
        buf.write(u"\u00b4\u00b6\u00b8\u00ba\u00bc\u00be\u00c0\u00c2\u00c4")
        buf.write(u"\u00c6\u00c8\u00ca\u00cc\u00ce\u00d0\u00d2\u00d4\u00d6")
        buf.write(u"\u00d8\u00da\u00dc\u00de\u00e0\u00e2\u00e4\u00e6\u00e8")
        buf.write(u"\u00ea\u00ec\u00ee\u00f0\u00f2\u00f4\u00f6\u00f8\u00fa")
        buf.write(u"\u00fc\u00fe\u0100\2\t\4\2\u0081\u0081\u00fc\u00fc\4")
        buf.write(u"\2\u0123\u0125\u012b\u012d\4\288ll\5\2\u0089\u0089\u00a7")
        buf.write(u"\u00a7\u00d9\u00d9\6\2<<ZZ\u00ad\u00ae\u00ed\u00ed\4")
        buf.write(u"\2\61\61qq\4\2\u011d\u011d\u011f\u011f\2\u04b7\2\u0102")
        buf.write(u"\3\2\2\2\4\u0104\3\2\2\2\6\u010a\3\2\2\2\b\u010e\3\2")
        buf.write(u"\2\2\n\u0117\3\2\2\2\f\u0119\3\2\2\2\16\u011b\3\2\2\2")
        buf.write(u"\20\u011d\3\2\2\2\22\u0120\3\2\2\2\24\u0124\3\2\2\2\26")
        buf.write(u"\u012c\3\2\2\2\30\u012e\3\2\2\2\32\u013b\3\2\2\2\34\u013d")
        buf.write(u"\3\2\2\2\36\u0148\3\2\2\2 \u014a\3\2\2\2\"\u014f\3\2")
        buf.write(u"\2\2$\u015b\3\2\2\2&\u0168\3\2\2\2(\u0171\3\2\2\2*\u0173")
        buf.write(u"\3\2\2\2,\u017e\3\2\2\2.\u0182\3\2\2\2\60\u0184\3\2\2")
        buf.write(u"\2\62\u0188\3\2\2\2\64\u018a\3\2\2\2\66\u0191\3\2\2\2")
        buf.write(u"8\u0195\3\2\2\2:\u0197\3\2\2\2<\u019c\3\2\2\2>\u01a1")
        buf.write(u"\3\2\2\2@\u01a3\3\2\2\2B\u01a5\3\2\2\2D\u01a9\3\2\2\2")
        buf.write(u"F\u01ac\3\2\2\2H\u01b0\3\2\2\2J\u01b4\3\2\2\2L\u01b8")
        buf.write(u"\3\2\2\2N\u01ba\3\2\2\2P\u01d5\3\2\2\2R\u01d7\3\2\2\2")
        buf.write(u"T\u01da\3\2\2\2V\u01e0\3\2\2\2X\u01e4\3\2\2\2Z\u01ed")
        buf.write(u"\3\2\2\2\\\u01ef\3\2\2\2^\u01fe\3\2\2\2`\u0200\3\2\2")
        buf.write(u"\2b\u0204\3\2\2\2d\u0206\3\2\2\2f\u020e\3\2\2\2h\u0213")
        buf.write(u"\3\2\2\2j\u0215\3\2\2\2l\u0221\3\2\2\2n\u0223\3\2\2\2")
        buf.write(u"p\u022a\3\2\2\2r\u0231\3\2\2\2t\u0233\3\2\2\2v\u0238")
        buf.write(u"\3\2\2\2x\u023f\3\2\2\2z\u0251\3\2\2\2|\u0261\3\2\2\2")
        buf.write(u"~\u0263\3\2\2\2\u0080\u02b2\3\2\2\2\u0082\u02b4\3\2\2")
        buf.write(u"\2\u0084\u02c8\3\2\2\2\u0086\u02cf\3\2\2\2\u0088\u02d9")
        buf.write(u"\3\2\2\2\u008a\u02df\3\2\2\2\u008c\u02e1\3\2\2\2\u008e")
        buf.write(u"\u02ea\3\2\2\2\u0090\u02f1\3\2\2\2\u0092\u02f8\3\2\2")
        buf.write(u"\2\u0094\u0315\3\2\2\2\u0096\u0317\3\2\2\2\u0098\u031a")
        buf.write(u"\3\2\2\2\u009a\u031e\3\2\2\2\u009c\u0320\3\2\2\2\u009e")
        buf.write(u"\u0322\3\2\2\2\u00a0\u0324\3\2\2\2\u00a2\u032b\3\2\2")
        buf.write(u"\2\u00a4\u0340\3\2\2\2\u00a6\u0344\3\2\2\2\u00a8\u0349")
        buf.write(u"\3\2\2\2\u00aa\u034e\3\2\2\2\u00ac\u0361\3\2\2\2\u00ae")
        buf.write(u"\u0365\3\2\2\2\u00b0\u036d\3\2\2\2\u00b2\u037a\3\2\2")
        buf.write(u"\2\u00b4\u037c\3\2\2\2\u00b6\u0381\3\2\2\2\u00b8\u0383")
        buf.write(u"\3\2\2\2\u00ba\u0385\3\2\2\2\u00bc\u0399\3\2\2\2\u00be")
        buf.write(u"\u039b\3\2\2\2\u00c0\u03aa\3\2\2\2\u00c2\u03b1\3\2\2")
        buf.write(u"\2\u00c4\u03b3\3\2\2\2\u00c6\u03b5\3\2\2\2\u00c8\u03b8")
        buf.write(u"\3\2\2\2\u00ca\u03ba\3\2\2\2\u00cc\u03bd\3\2\2\2\u00ce")
        buf.write(u"\u03c3\3\2\2\2\u00d0\u03c5\3\2\2\2\u00d2\u03c9\3\2\2")
        buf.write(u"\2\u00d4\u03d1\3\2\2\2\u00d6\u03d3\3\2\2\2\u00d8\u03d7")
        buf.write(u"\3\2\2\2\u00da\u03d9\3\2\2\2\u00dc\u03dd\3\2\2\2\u00de")
        buf.write(u"\u03f0\3\2\2\2\u00e0\u0400\3\2\2\2\u00e2\u0413\3\2\2")
        buf.write(u"\2\u00e4\u0415\3\2\2\2\u00e6\u0455\3\2\2\2\u00e8\u0457")
        buf.write(u"\3\2\2\2\u00ea\u0459\3\2\2\2\u00ec\u045b\3\2\2\2\u00ee")
        buf.write(u"\u045f\3\2\2\2\u00f0\u0464\3\2\2\2\u00f2\u0466\3\2\2")
        buf.write(u"\2\u00f4\u0468\3\2\2\2\u00f6\u0476\3\2\2\2\u00f8\u0478")
        buf.write(u"\3\2\2\2\u00fa\u047e\3\2\2\2\u00fc\u0487\3\2\2\2\u00fe")
        buf.write(u"\u0489\3\2\2\2\u0100\u048c\3\2\2\2\u0102\u0103\7\u0114")
        buf.write(u"\2\2\u0103\3\3\2\2\2\u0104\u0105\7\5\2\2\u0105\u0106")
        buf.write(u"\7\u011a\2\2\u0106\u0107\5^\60\2\u0107\u0108\7\u011b")
        buf.write(u"\2\2\u0108\5\3\2\2\2\u0109\u010b\7\67\2\2\u010a\u0109")
        buf.write(u"\3\2\2\2\u010a\u010b\3\2\2\2\u010b\u010c\3\2\2\2\u010c")
        buf.write(u"\u010d\5(\25\2\u010d\7\3\2\2\2\u010e\u0110\5\u00fa~\2")
        buf.write(u"\u010f\u0111\7\u00b8\2\2\u0110\u010f\3\2\2\2\u0110\u0111")
        buf.write(u"\3\2\2\2\u0111\u0112\3\2\2\2\u0112\u0113\7>\2\2\u0113")
        buf.write(u"\u0114\5\u00fa~\2\u0114\u0115\7\64\2\2\u0115\u0116\5")
        buf.write(u"\u00fa~\2\u0116\t\3\2\2\2\u0117\u0118\7\u0117\2\2\u0118")
        buf.write(u"\13\3\2\2\2\u0119\u011a\7\u0118\2\2\u011a\r\3\2\2\2\u011b")
        buf.write(u"\u011c\7\u0127\2\2\u011c\17\3\2\2\2\u011d\u011e\7\u0119")
        buf.write(u"\2\2\u011e\21\3\2\2\2\u011f\u0121\7\u00b8\2\2\u0120\u011f")
        buf.write(u"\3\2\2\2\u0120\u0121\3\2\2\2\u0121\u0122\3\2\2\2\u0122")
        buf.write(u"\u0123\5\26\f\2\u0123\23\3\2\2\2\u0124\u0125\t\2\2\2")
        buf.write(u"\u0125\25\3\2\2\2\u0126\u0127\7\u011a\2\2\u0127\u0128")
        buf.write(u"\5\u00ba^\2\u0128\u0129\7\u011b\2\2\u0129\u012d\3\2\2")
        buf.write(u"\2\u012a\u012d\5\u00a4S\2\u012b\u012d\5\32\16\2\u012c")
        buf.write(u"\u0126\3\2\2\2\u012c\u012a\3\2\2\2\u012c\u012b\3\2\2")
        buf.write(u"\2\u012d\27\3\2\2\2\u012e\u012f\b\r\1\2\u012f\u0130\5")
        buf.write(u"\22\n\2\u0130\u0136\3\2\2\2\u0131\u0132\f\3\2\2\u0132")
        buf.write(u"\u0133\7\64\2\2\u0133\u0135\5\22\n\2\u0134\u0131\3\2")
        buf.write(u"\2\2\u0135\u0138\3\2\2\2\u0136\u0134\3\2\2\2\u0136\u0137")
        buf.write(u"\3\2\2\2\u0137\31\3\2\2\2\u0138\u0136\3\2\2\2\u0139\u013c")
        buf.write(u"\5\24\13\2\u013a\u013c\5\u00f4{\2\u013b\u0139\3\2\2\2")
        buf.write(u"\u013b\u013a\3\2\2\2\u013c\33\3\2\2\2\u013d\u013e\7\r")
        buf.write(u"\2\2\u013e\u013f\7\u011a\2\2\u013f\u0140\5\66\34\2\u0140")
        buf.write(u"\u0141\7\u011e\2\2\u0141\u0142\5B\"\2\u0142\u0143\7\u011e")
        buf.write(u"\2\2\u0143\u0144\5\u0092J\2\u0144\u0145\7\u011e\2\2\u0145")
        buf.write(u"\u0146\5\u0092J\2\u0146\u0147\7\u011b\2\2\u0147\35\3")
        buf.write(u"\2\2\2\u0148\u0149\7\u0116\2\2\u0149\37\3\2\2\2\u014a")
        buf.write(u"\u014b\7\17\2\2\u014b\u014c\7\u011a\2\2\u014c\u014d\5")
        buf.write(u"^\60\2\u014d\u014e\7\u011b\2\2\u014e!\3\2\2\2\u014f\u0153")
        buf.write(u"\7\u012f\2\2\u0150\u0152\7\u0116\2\2\u0151\u0150\3\2")
        buf.write(u"\2\2\u0152\u0155\3\2\2\2\u0153\u0151\3\2\2\2\u0153\u0154")
        buf.write(u"\3\2\2\2\u0154\u0156\3\2\2\2\u0155\u0153\3\2\2\2\u0156")
        buf.write(u"\u0157\7\u012f\2\2\u0157#\3\2\2\2\u0158\u0159\b\23\1")
        buf.write(u"\2\u0159\u015c\5\u00fc\177\2\u015a\u015c\5\u00d8m\2\u015b")
        buf.write(u"\u0158\3\2\2\2\u015b\u015a\3\2\2\2\u015c\u0165\3\2\2")
        buf.write(u"\2\u015d\u015e\f\5\2\2\u015e\u0161\5\62\32\2\u015f\u0162")
        buf.write(u"\5\u00fc\177\2\u0160\u0162\5\u00d8m\2\u0161\u015f\3\2")
        buf.write(u"\2\2\u0161\u0160\3\2\2\2\u0162\u0164\3\2\2\2\u0163\u015d")
        buf.write(u"\3\2\2\2\u0164\u0167\3\2\2\2\u0165\u0163\3\2\2\2\u0165")
        buf.write(u"\u0166\3\2\2\2\u0166%\3\2\2\2\u0167\u0165\3\2\2\2\u0168")
        buf.write(u"\u0169\7\20\2\2\u0169\u016a\7\u011a\2\2\u016a\u016b\5")
        buf.write(u"\66\34\2\u016b\u016c\7\u011e\2\2\u016c\u016d\5B\"\2\u016d")
        buf.write(u"\u016e\7\u011e\2\2\u016e\u016f\5\u00b2Z\2\u016f\u0170")
        buf.write(u"\7\u011b\2\2\u0170\'\3\2\2\2\u0171\u0172\5h\65\2\u0172")
        buf.write(u")\3\2\2\2\u0173\u0178\5(\25\2\u0174\u0175\7\u011e\2\2")
        buf.write(u"\u0175\u0177\5(\25\2\u0176\u0174\3\2\2\2\u0177\u017a")
        buf.write(u"\3\2\2\2\u0178\u0176\3\2\2\2\u0178\u0179\3\2\2\2\u0179")
        buf.write(u"+\3\2\2\2\u017a\u0178\3\2\2\2\u017b\u017c\5\u00a8U\2")
        buf.write(u"\u017c\u017d\7\u0120\2\2\u017d\u017f\3\2\2\2\u017e\u017b")
        buf.write(u"\3\2\2\2\u017e\u017f\3\2\2\2\u017f\u0180\3\2\2\2\u0180")
        buf.write(u"\u0181\5(\25\2\u0181-\3\2\2\2\u0182\u0183\t\3\2\2\u0183")
        buf.write(u"/\3\2\2\2\u0184\u0185\5\u00fa~\2\u0185\u0186\5.\30\2")
        buf.write(u"\u0186\u0187\5\u00fa~\2\u0187\61\3\2\2\2\u0188\u0189")
        buf.write(u"\7\u012a\2\2\u0189\63\3\2\2\2\u018a\u018b\7\21\2\2\u018b")
        buf.write(u"\u018c\7\u011a\2\2\u018c\u018d\5^\60\2\u018d\u018e\7")
        buf.write(u"\u011e\2\2\u018e\u018f\5^\60\2\u018f\u0190\7\u011b\2")
        buf.write(u"\2\u0190\65\3\2\2\2\u0191\u0192\5\u00d6l\2\u0192\67\3")
        buf.write(u"\2\2\2\u0193\u0196\5\u00a0Q\2\u0194\u0196\5,\27\2\u0195")
        buf.write(u"\u0193\3\2\2\2\u0195\u0194\3\2\2\2\u01969\3\2\2\2\u0197")
        buf.write(u"\u0198\7\22\2\2\u0198\u0199\7\u011a\2\2\u0199\u019a\5")
        buf.write(u"8\35\2\u019a\u019b\7\u011b\2\2\u019b;\3\2\2\2\u019c\u019d")
        buf.write(u"\7\23\2\2\u019d\u019e\7\u011a\2\2\u019e\u019f\58\35\2")
        buf.write(u"\u019f\u01a0\7\u011b\2\2\u01a0=\3\2\2\2\u01a1\u01a2\5")
        buf.write(u"\u0092J\2\u01a2?\3\2\2\2\u01a3\u01a4\5\u0092J\2\u01a4")
        buf.write(u"A\3\2\2\2\u01a5\u01a6\5> \2\u01a6\u01a7\7\u011e\2\2\u01a7")
        buf.write(u"\u01a8\5@!\2\u01a8C\3\2\2\2\u01a9\u01aa\5h\65\2\u01aa")
        buf.write(u"E\3\2\2\2\u01ab\u01ad\7\67\2\2\u01ac\u01ab\3\2\2\2\u01ac")
        buf.write(u"\u01ad\3\2\2\2\u01ad\u01ae\3\2\2\2\u01ae\u01af\5D#\2")
        buf.write(u"\u01afG\3\2\2\2\u01b0\u01b1\7\u012e\2\2\u01b1\u01b2\7")
        buf.write(u"\u0116\2\2\u01b2\u01b3\7\u012e\2\2\u01b3I\3\2\2\2\u01b4")
        buf.write(u"\u01b6\5\u00fa~\2\u01b5\u01b7\5\6\4\2\u01b6\u01b5\3\2")
        buf.write(u"\2\2\u01b6\u01b7\3\2\2\2\u01b7K\3\2\2\2\u01b8\u01b9\5")
        buf.write(u"\u00e2r\2\u01b9M\3\2\2\2\u01ba\u01bb\7\30\2\2\u01bb\u01c8")
        buf.write(u"\7\u011a\2\2\u01bc\u01bd\58\35\2\u01bd\u01be\7\u011e")
        buf.write(u"\2\2\u01be\u01bf\58\35\2\u01bf\u01c9\3\2\2\2\u01c0\u01c1")
        buf.write(u"\5\u0092J\2\u01c1\u01c2\7\u011e\2\2\u01c2\u01c3\5\u0092")
        buf.write(u"J\2\u01c3\u01c4\7\u011e\2\2\u01c4\u01c5\5\u0092J\2\u01c5")
        buf.write(u"\u01c6\7\u011e\2\2\u01c6\u01c7\5\u0092J\2\u01c7\u01c9")
        buf.write(u"\3\2\2\2\u01c8\u01bc\3\2\2\2\u01c8\u01c0\3\2\2\2\u01c9")
        buf.write(u"\u01ca\3\2\2\2\u01ca\u01cb\7\u011b\2\2\u01cbO\3\2\2\2")
        buf.write(u"\u01cc\u01d1\5\u00eav\2\u01cd\u01cf\7\u0120\2\2\u01ce")
        buf.write(u"\u01d0\5\u00eav\2\u01cf\u01ce\3\2\2\2\u01cf\u01d0\3\2")
        buf.write(u"\2\2\u01d0\u01d2\3\2\2\2\u01d1\u01cd\3\2\2\2\u01d1\u01d2")
        buf.write(u"\3\2\2\2\u01d2\u01d6\3\2\2\2\u01d3\u01d4\7\u0120\2\2")
        buf.write(u"\u01d4\u01d6\5\u00eav\2\u01d5\u01cc\3\2\2\2\u01d5\u01d3")
        buf.write(u"\3\2\2\2\u01d6Q\3\2\2\2\u01d7\u01d8\7~\2\2\u01d8\u01d9")
        buf.write(u"\5\u00e2r\2\u01d9S\3\2\2\2\u01da\u01db\7\24\2\2\u01db")
        buf.write(u"\u01dc\7\u011a\2\2\u01dc\u01dd\5^\60\2\u01dd\u01de\7")
        buf.write(u"\u011b\2\2\u01deU\3\2\2\2\u01df\u01e1\5\u00caf\2\u01e0")
        buf.write(u"\u01df\3\2\2\2\u01e0\u01e1\3\2\2\2\u01e1\u01e2\3\2\2")
        buf.write(u"\2\u01e2\u01e3\5\u0090I\2\u01e3W\3\2\2\2\u01e4\u01e5")
        buf.write(u"\7\u0088\2\2\u01e5\u01ea\5\u00e0q\2\u01e6\u01e7\7\u011e")
        buf.write(u"\2\2\u01e7\u01e9\5\u00e0q\2\u01e8\u01e6\3\2\2\2\u01e9")
        buf.write(u"\u01ec\3\2\2\2\u01ea\u01e8\3\2\2\2\u01ea\u01eb\3\2\2")
        buf.write(u"\2\u01ebY\3\2\2\2\u01ec\u01ea\3\2\2\2\u01ed\u01ee\5\"")
        buf.write(u"\22\2\u01ee[\3\2\2\2\u01ef\u01f0\5\u00c4c\2\u01f0\u01f2")
        buf.write(u"\7\u011a\2\2\u01f1\u01f3\5\u00c8e\2\u01f2\u01f1\3\2\2")
        buf.write(u"\2\u01f2\u01f3\3\2\2\2\u01f3\u01f4\3\2\2\2\u01f4\u01f5")
        buf.write(u"\5\u00fa~\2\u01f5\u01f6\7\u011b\2\2\u01f6]\3\2\2\2\u01f7")
        buf.write(u"\u01ff\5\34\17\2\u01f8\u01ff\5 \21\2\u01f9\u01ff\5&\24")
        buf.write(u"\2\u01fa\u01ff\5\u00a0Q\2\u01fb\u01ff\5\u00a2R\2\u01fc")
        buf.write(u"\u01ff\5\u00b4[\2\u01fd\u01ff\5\u00f4{\2\u01fe\u01f7")
        buf.write(u"\3\2\2\2\u01fe\u01f8\3\2\2\2\u01fe\u01f9\3\2\2\2\u01fe")
        buf.write(u"\u01fa\3\2\2\2\u01fe\u01fb\3\2\2\2\u01fe\u01fc\3\2\2")
        buf.write(u"\2\u01fe\u01fd\3\2\2\2\u01ff_\3\2\2\2\u0200\u0201\7\u008f")
        buf.write(u"\2\2\u0201\u0202\7B\2\2\u0202\u0203\5d\63\2\u0203a\3")
        buf.write(u"\2\2\2\u0204\u0205\5,\27\2\u0205c\3\2\2\2\u0206\u020b")
        buf.write(u"\5b\62\2\u0207\u0208\7\u011e\2\2\u0208\u020a\5b\62\2")
        buf.write(u"\u0209\u0207\3\2\2\2\u020a\u020d\3\2\2\2\u020b\u0209")
        buf.write(u"\3\2\2\2\u020b\u020c\3\2\2\2\u020ce\3\2\2\2\u020d\u020b")
        buf.write(u"\3\2\2\2\u020e\u020f\7\u0090\2\2\u020f\u0210\5\u00ba")
        buf.write(u"^\2\u0210g\3\2\2\2\u0211\u0214\5\u00b6\\\2\u0212\u0214")
        buf.write(u"\5H%\2\u0213\u0211\3\2\2\2\u0213\u0212\3\2\2\2\u0214")
        buf.write(u"i\3\2\2\2\u0215\u0217\5\u00fa~\2\u0216\u0218\7\u00b8")
        buf.write(u"\2\2\u0217\u0216\3\2\2\2\u0217\u0218\3\2\2\2\u0218\u0219")
        buf.write(u"\3\2\2\2\u0219\u021a\7\u0094\2\2\u021a\u021b\5l\67\2")
        buf.write(u"\u021bk\3\2\2\2\u021c\u0222\5\u00e2r\2\u021d\u021e\7")
        buf.write(u"\u011a\2\2\u021e\u021f\5n8\2\u021f\u0220\7\u011b\2\2")
        buf.write(u"\u0220\u0222\3\2\2\2\u0221\u021c\3\2\2\2\u0221\u021d")
        buf.write(u"\3\2\2\2\u0222m\3\2\2\2\u0223\u0226\5\u00fa~\2\u0224")
        buf.write(u"\u0225\7\u011e\2\2\u0225\u0227\5\u00fa~\2\u0226\u0224")
        buf.write(u"\3\2\2\2\u0227\u0228\3\2\2\2\u0228\u0226\3\2\2\2\u0228")
        buf.write(u"\u0229\3\2\2\2\u0229o\3\2\2\2\u022a\u022b\7\34\2\2\u022b")
        buf.write(u"\u022c\7\u011a\2\2\u022c\u022d\5^\60\2\u022d\u022e\7")
        buf.write(u"\u011e\2\2\u022e\u022f\5^\60\2\u022f\u0230\7\u011b\2")
        buf.write(u"\2\u0230q\3\2\2\2\u0231\u0232\5*\26\2\u0232s\3\2\2\2")
        buf.write(u"\u0233\u0234\7\u00bf\2\2\u0234\u0235\5\u00ba^\2\u0235")
        buf.write(u"u\3\2\2\2\u0236\u0239\5t;\2\u0237\u0239\5\u0082B\2\u0238")
        buf.write(u"\u0236\3\2\2\2\u0238\u0237\3\2\2\2\u0239w\3\2\2\2\u023a")
        buf.write(u"\u0240\7\u0097\2\2\u023b\u023d\5\u009cO\2\u023c\u023e")
        buf.write(u"\7\u00c5\2\2\u023d\u023c\3\2\2\2\u023d\u023e\3\2\2\2")
        buf.write(u"\u023e\u0240\3\2\2\2\u023f\u023a\3\2\2\2\u023f\u023b")
        buf.write(u"\3\2\2\2\u0240y\3\2\2\2\u0241\u0243\5\u00e0q\2\u0242")
        buf.write(u"\u0244\7\u00b4\2\2\u0243\u0242\3\2\2\2\u0243\u0244\3")
        buf.write(u"\2\2\2\u0244\u0246\3\2\2\2\u0245\u0247\5x=\2\u0246\u0245")
        buf.write(u"\3\2\2\2\u0246\u0247\3\2\2\2\u0247\u0248\3\2\2\2\u0248")
        buf.write(u"\u0249\7\u00a2\2\2\u0249\u024b\5\u00e0q\2\u024a\u024c")
        buf.write(u"\5v<\2\u024b\u024a\3\2\2\2\u024b\u024c\3\2\2\2\u024c")
        buf.write(u"\u0252\3\2\2\2\u024d\u024e\7\u011a\2\2\u024e\u024f\5")
        buf.write(u"z>\2\u024f\u0250\7\u011b\2\2\u0250\u0252\3\2\2\2\u0251")
        buf.write(u"\u0241\3\2\2\2\u0251\u024d\3\2\2\2\u0252{\3\2\2\2\u0253")
        buf.write(u"\u0255\5~@\2\u0254\u0256\7\u00b8\2\2\u0255\u0254\3\2")
        buf.write(u"\2\2\u0255\u0256\3\2\2\2\u0256\u0257\3\2\2\2\u0257\u0258")
        buf.write(u"\7\u00a9\2\2\u0258\u0259\5\u009eP\2\u0259\u0262\3\2\2")
        buf.write(u"\2\u025a\u025c\5~@\2\u025b\u025d\7\u00b8\2\2\u025c\u025b")
        buf.write(u"\3\2\2\2\u025c\u025d\3\2\2\2\u025d\u025e\3\2\2\2\u025e")
        buf.write(u"\u025f\7\33\2\2\u025f\u0260\5\u009eP\2\u0260\u0262\3")
        buf.write(u"\2\2\2\u0261\u0253\3\2\2\2\u0261\u025a\3\2\2\2\u0262")
        buf.write(u"}\3\2\2\2\u0263\u0264\5$\23\2\u0264\177\3\2\2\2\u0265")
        buf.write(u"\u0266\7\3\2\2\u0266\u0267\7\u011a\2\2\u0267\u0268\5")
        buf.write(u"\u0092J\2\u0268\u0269\7\u011b\2\2\u0269\u02b3\3\2\2\2")
        buf.write(u"\u026a\u026b\7\16\2\2\u026b\u026c\7\u011a\2\2\u026c\u026d")
        buf.write(u"\5\u0092J\2\u026d\u026e\7\u011b\2\2\u026e\u02b3\3\2\2")
        buf.write(u"\2\u026f\u0270\7\27\2\2\u0270\u0271\7\u011a\2\2\u0271")
        buf.write(u"\u0272\5\u0092J\2\u0272\u0273\7\u011b\2\2\u0273\u02b3")
        buf.write(u"\3\2\2\2\u0274\u0275\7\31\2\2\u0275\u0276\7\u011a\2\2")
        buf.write(u"\u0276\u0277\5\u0092J\2\u0277\u0278\7\u011b\2\2\u0278")
        buf.write(u"\u02b3\3\2\2\2\u0279\u027a\7\32\2\2\u027a\u027b\7\u011a")
        buf.write(u"\2\2\u027b\u027c\5\u0092J\2\u027c\u027d\7\u011b\2\2\u027d")
        buf.write(u"\u02b3\3\2\2\2\u027e\u027f\7\36\2\2\u027f\u0280\7\u011a")
        buf.write(u"\2\2\u0280\u0281\5\u0092J\2\u0281\u0282\7\u011b\2\2\u0282")
        buf.write(u"\u02b3\3\2\2\2\u0283\u0284\7\37\2\2\u0284\u0285\7\u011a")
        buf.write(u"\2\2\u0285\u0286\5\u0092J\2\u0286\u0287\7\u011b\2\2\u0287")
        buf.write(u"\u02b3\3\2\2\2\u0288\u0289\7 \2\2\u0289\u028a\7\u011a")
        buf.write(u"\2\2\u028a\u028b\5\u0092J\2\u028b\u028c\7\u011e\2\2\u028c")
        buf.write(u"\u028d\5\u0092J\2\u028d\u028e\7\u011b\2\2\u028e\u02b3")
        buf.write(u"\3\2\2\2\u028f\u0290\7!\2\2\u0290\u0291\7\u011a\2\2\u0291")
        buf.write(u"\u02b3\7\u011b\2\2\u0292\u0293\7$\2\2\u0293\u0294\7\u011a")
        buf.write(u"\2\2\u0294\u0295\5\u0092J\2\u0295\u0296\7\u011e\2\2\u0296")
        buf.write(u"\u0297\5\u0092J\2\u0297\u0298\7\u011b\2\2\u0298\u02b3")
        buf.write(u"\3\2\2\2\u0299\u029a\7%\2\2\u029a\u029b\7\u011a\2\2\u029b")
        buf.write(u"\u029c\5\u0092J\2\u029c\u029d\7\u011b\2\2\u029d\u02b3")
        buf.write(u"\3\2\2\2\u029e\u029f\7%\2\2\u029f\u02a1\7\u011a\2\2\u02a0")
        buf.write(u"\u02a2\5\u00eav\2\u02a1\u02a0\3\2\2\2\u02a1\u02a2\3\2")
        buf.write(u"\2\2\u02a2\u02a3\3\2\2\2\u02a3\u02b3\7\u011b\2\2\u02a4")
        buf.write(u"\u02a5\7*\2\2\u02a5\u02a6\7\u011a\2\2\u02a6\u02a7\5\u0092")
        buf.write(u"J\2\u02a7\u02a8\7\u011b\2\2\u02a8\u02b3\3\2\2\2\u02a9")
        buf.write(u"\u02aa\7-\2\2\u02aa\u02ab\7\u011a\2\2\u02ab\u02ae\5\u0092")
        buf.write(u"J\2\u02ac\u02ad\7\u011e\2\2\u02ad\u02af\5\u00ccg\2\u02ae")
        buf.write(u"\u02ac\3\2\2\2\u02ae\u02af\3\2\2\2\u02af\u02b0\3\2\2")
        buf.write(u"\2\u02b0\u02b1\7\u011b\2\2\u02b1\u02b3\3\2\2\2\u02b2")
        buf.write(u"\u0265\3\2\2\2\u02b2\u026a\3\2\2\2\u02b2\u026f\3\2\2")
        buf.write(u"\2\u02b2\u0274\3\2\2\2\u02b2\u0279\3\2\2\2\u02b2\u027e")
        buf.write(u"\3\2\2\2\u02b2\u0283\3\2\2\2\u02b2\u0288\3\2\2\2\u02b2")
        buf.write(u"\u028f\3\2\2\2\u02b2\u0292\3\2\2\2\u02b2\u0299\3\2\2")
        buf.write(u"\2\u02b2\u029e\3\2\2\2\u02b2\u02a4\3\2\2\2\u02b2\u02a9")
        buf.write(u"\3\2\2\2\u02b3\u0081\3\2\2\2\u02b4\u02b5\7\u0104\2\2")
        buf.write(u"\u02b5\u02b6\7\u011a\2\2\u02b6\u02b7\5r:\2\u02b7\u02b8")
        buf.write(u"\7\u011b\2\2\u02b8\u0083\3\2\2\2\u02b9\u02c9\5\u0088")
        buf.write(u"E\2\u02ba\u02bb\5\u00aaV\2\u02bb\u02bd\7\u00fd\2\2\u02bc")
        buf.write(u"\u02be\7\61\2\2\u02bd\u02bc\3\2\2\2\u02bd\u02be\3\2\2")
        buf.write(u"\2\u02be\u02bf\3\2\2\2\u02bf\u02c0\5\u00b0Y\2\u02c0\u02c9")
        buf.write(u"\3\2\2\2\u02c1\u02c2\5\u00aaV\2\u02c2\u02c4\7z\2\2\u02c3")
        buf.write(u"\u02c5\7\61\2\2\u02c4\u02c3\3\2\2\2\u02c4\u02c5\3\2\2")
        buf.write(u"\2\u02c5\u02c6\3\2\2\2\u02c6\u02c7\5\u00b0Y\2\u02c7\u02c9")
        buf.write(u"\3\2\2\2\u02c8\u02b9\3\2\2\2\u02c8\u02ba\3\2\2\2\u02c8")
        buf.write(u"\u02c1\3\2\2\2\u02c9\u0085\3\2\2\2\u02ca\u02d0\5\u00ae")
        buf.write(u"X\2\u02cb\u02cc\7\u011a\2\2\u02cc\u02cd\5\u0084C\2\u02cd")
        buf.write(u"\u02ce\7\u011b\2\2\u02ce\u02d0\3\2\2\2\u02cf\u02ca\3")
        buf.write(u"\2\2\2\u02cf\u02cb\3\2\2\2\u02d0\u0087\3\2\2\2\u02d1")
        buf.write(u"\u02da\5\u0086D\2\u02d2\u02d3\5\u00b0Y\2\u02d3\u02d5")
        buf.write(u"\7\u009d\2\2\u02d4\u02d6\7\61\2\2\u02d5\u02d4\3\2\2\2")
        buf.write(u"\u02d5\u02d6\3\2\2\2\u02d6\u02d7\3\2\2\2\u02d7\u02d8")
        buf.write(u"\5\u00aaV\2\u02d8\u02da\3\2\2\2\u02d9\u02d1\3\2\2\2\u02d9")
        buf.write(u"\u02d2\3\2\2\2\u02da\u0089\3\2\2\2\u02db\u02e0\5\4\3")
        buf.write(u"\2\u02dc\u02e0\5:\36\2\u02dd\u02e0\5<\37\2\u02de\u02e0")
        buf.write(u"\5N(\2\u02df\u02db\3\2\2\2\u02df\u02dc\3\2\2\2\u02df")
        buf.write(u"\u02dd\3\2\2\2\u02df\u02de\3\2\2\2\u02e0\u008b\3\2\2")
        buf.write(u"\2\u02e1\u02e2\5,\27\2\u02e2\u02e4\7\u00a0\2\2\u02e3")
        buf.write(u"\u02e5\7\u00b8\2\2\u02e4\u02e3\3\2\2\2\u02e4\u02e5\3")
        buf.write(u"\2\2\2\u02e5\u02e6\3\2\2\2\u02e6\u02e7\7\u00b9\2\2\u02e7")
        buf.write(u"\u008d\3\2\2\2\u02e8\u02eb\5\u00a6T\2\u02e9\u02eb\5\u008a")
        buf.write(u"F\2\u02ea\u02e8\3\2\2\2\u02ea\u02e9\3\2\2\2\u02eb\u008f")
        buf.write(u"\3\2\2\2\u02ec\u02ee\5\u00caf\2\u02ed\u02ec\3\2\2\2\u02ed")
        buf.write(u"\u02ee\3\2\2\2\u02ee\u02ef\3\2\2\2\u02ef\u02f2\5\u00fc")
        buf.write(u"\177\2\u02f0\u02f2\5\u0094K\2\u02f1\u02ed\3\2\2\2\u02f1")
        buf.write(u"\u02f0\3\2\2\2\u02f2\u0091\3\2\2\2\u02f3\u02f4\bJ\1\2")
        buf.write(u"\u02f4\u02f9\5\u00e4s\2\u02f5\u02f6\5\f\7\2\u02f6\u02f7")
        buf.write(u"\5\u0092J\b\u02f7\u02f9\3\2\2\2\u02f8\u02f3\3\2\2\2\u02f8")
        buf.write(u"\u02f5\3\2\2\2\u02f9\u030e\3\2\2\2\u02fa\u02fb\f\7\2")
        buf.write(u"\2\u02fb\u02fc\5\n\6\2\u02fc\u02fd\5\u0092J\b\u02fd\u030d")
        buf.write(u"\3\2\2\2\u02fe\u02ff\f\6\2\2\u02ff\u0300\5\16\b\2\u0300")
        buf.write(u"\u0301\5\u0092J\7\u0301\u030d\3\2\2\2\u0302\u0303\f\5")
        buf.write(u"\2\2\u0303\u0304\5\20\t\2\u0304\u0305\5\u0092J\6\u0305")
        buf.write(u"\u030d\3\2\2\2\u0306\u0307\f\4\2\2\u0307\u0308\7\u011d")
        buf.write(u"\2\2\u0308\u030d\5\u00e4s\2\u0309\u030a\f\3\2\2\u030a")
        buf.write(u"\u030b\7\u011f\2\2\u030b\u030d\5\u00e4s\2\u030c\u02fa")
        buf.write(u"\3\2\2\2\u030c\u02fe\3\2\2\2\u030c\u0302\3\2\2\2\u030c")
        buf.write(u"\u0306\3\2\2\2\u030c\u0309\3\2\2\2\u030d\u0310\3\2\2")
        buf.write(u"\2\u030e\u030c\3\2\2\2\u030e\u030f\3\2\2\2\u030f\u0093")
        buf.write(u"\3\2\2\2\u0310\u030e\3\2\2\2\u0311\u0316\5\u00e6t\2\u0312")
        buf.write(u"\u0316\5\u0080A\2\u0313\u0316\5\u008eH\2\u0314\u0316")
        buf.write(u"\5\u00f4{\2\u0315\u0311\3\2\2\2\u0315\u0312\3\2\2\2\u0315")
        buf.write(u"\u0313\3\2\2\2\u0315\u0314\3\2\2\2\u0316\u0095\3\2\2")
        buf.write(u"\2\u0317\u0318\7\u00be\2\2\u0318\u0319\5\u00eav\2\u0319")
        buf.write(u"\u0097\3\2\2\2\u031a\u031b\7\u00c4\2\2\u031b\u031c\7")
        buf.write(u"B\2\2\u031c\u031d\5\u00d2j\2\u031d\u0099\3\2\2\2\u031e")
        buf.write(u"\u031f\t\4\2\2\u031f\u009b\3\2\2\2\u0320\u0321\t\5\2")
        buf.write(u"\2\u0321\u009d\3\2\2\2\u0322\u0323\5$\23\2\u0323\u009f")
        buf.write(u"\3\2\2\2\u0324\u0325\7\"\2\2\u0325\u0326\7\u011a\2\2")
        buf.write(u"\u0326\u0327\5\66\34\2\u0327\u0328\7\u011e\2\2\u0328")
        buf.write(u"\u0329\5B\"\2\u0329\u032a\7\u011b\2\2\u032a\u00a1\3\2")
        buf.write(u"\2\2\u032b\u032c\7#\2\2\u032c\u032d\7\u011a\2\2\u032d")
        buf.write(u"\u032e\5\66\34\2\u032e\u032f\7\u011e\2\2\u032f\u0330")
        buf.write(u"\5B\"\2\u0330\u0331\7\u011e\2\2\u0331\u0334\5B\"\2\u0332")
        buf.write(u"\u0333\7\u011e\2\2\u0333\u0335\5B\"\2\u0334\u0332\3\2")
        buf.write(u"\2\2\u0335\u0336\3\2\2\2\u0336\u0334\3\2\2\2\u0336\u0337")
        buf.write(u"\3\2\2\2\u0337\u0338\3\2\2\2\u0338\u0339\7\u011b\2\2")
        buf.write(u"\u0339\u00a3\3\2\2\2\u033a\u0341\5\60\31\2\u033b\u0341")
        buf.write(u"\5\b\5\2\u033c\u0341\5j\66\2\u033d\u0341\5|?\2\u033e")
        buf.write(u"\u0341\5\u008cG\2\u033f\u0341\5R*\2\u0340\u033a\3\2\2")
        buf.write(u"\2\u0340\u033b\3\2\2\2\u0340\u033c\3\2\2\2\u0340\u033d")
        buf.write(u"\3\2\2\2\u0340\u033e\3\2\2\2\u0340\u033f\3\2\2\2\u0341")
        buf.write(u"\u00a5\3\2\2\2\u0342\u0345\5\64\33\2\u0343\u0345\5p9")
        buf.write(u"\2\u0344\u0342\3\2\2\2\u0344\u0343\3\2\2\2\u0345\u00a7")
        buf.write(u"\3\2\2\2\u0346\u034a\5(\25\2\u0347\u034a\5\u00dep\2\u0348")
        buf.write(u"\u034a\5D#\2\u0349\u0346\3\2\2\2\u0349\u0347\3\2\2\2")
        buf.write(u"\u0349\u0348\3\2\2\2\u034a\u00a9\3\2\2\2\u034b\u034c")
        buf.write(u"\bV\1\2\u034c\u034f\5\u0088E\2\u034d\u034f\5z>\2\u034e")
        buf.write(u"\u034b\3\2\2\2\u034e\u034d\3\2\2\2\u034f\u035e\3\2\2")
        buf.write(u"\2\u0350\u0351\f\5\2\2\u0351\u0353\7\u00fd\2\2\u0352")
        buf.write(u"\u0354\7\61\2\2\u0353\u0352\3\2\2\2\u0353\u0354\3\2\2")
        buf.write(u"\2\u0354\u0355\3\2\2\2\u0355\u035d\5\u00b0Y\2\u0356\u0357")
        buf.write(u"\f\4\2\2\u0357\u0359\7z\2\2\u0358\u035a\7\61\2\2\u0359")
        buf.write(u"\u0358\3\2\2\2\u0359\u035a\3\2\2\2\u035a\u035b\3\2\2")
        buf.write(u"\2\u035b\u035d\5\u00b0Y\2\u035c\u0350\3\2\2\2\u035c\u0356")
        buf.write(u"\3\2\2\2\u035d\u0360\3\2\2\2\u035e\u035c\3\2\2\2\u035e")
        buf.write(u"\u035f\3\2\2\2\u035f\u00ab\3\2\2\2\u0360\u035e\3\2\2")
        buf.write(u"\2\u0361\u0362\7\u0116\2\2\u0362\u00ad\3\2\2\2\u0363")
        buf.write(u"\u0364\7\u010d\2\2\u0364\u0366\5\u0100\u0081\2\u0365")
        buf.write(u"\u0363\3\2\2\2\u0365\u0366\3\2\2\2\u0366\u0367\3\2\2")
        buf.write(u"\2\u0367\u0368\5\u00be`\2\u0368\u0369\7\u0122\2\2\u0369")
        buf.write(u"\u00af\3\2\2\2\u036a\u036b\bY\1\2\u036b\u036e\5\u0086")
        buf.write(u"D\2\u036c\u036e\5z>\2\u036d\u036a\3\2\2\2\u036d\u036c")
        buf.write(u"\3\2\2\2\u036e\u0377\3\2\2\2\u036f\u0370\f\4\2\2\u0370")
        buf.write(u"\u0372\7\u009d\2\2\u0371\u0373\7\61\2\2\u0372\u0371\3")
        buf.write(u"\2\2\2\u0372\u0373\3\2\2\2\u0373\u0374\3\2\2\2\u0374")
        buf.write(u"\u0376\5\u00aaV\2\u0375\u036f\3\2\2\2\u0376\u0379\3\2")
        buf.write(u"\2\2\u0377\u0375\3\2\2\2\u0377\u0378\3\2\2\2\u0378\u00b1")
        buf.write(u"\3\2\2\2\u0379\u0377\3\2\2\2\u037a\u037b\5\u0092J\2\u037b")
        buf.write(u"\u00b3\3\2\2\2\u037c\u037d\7&\2\2\u037d\u037e\7\u011a")
        buf.write(u"\2\2\u037e\u037f\5\u00d6l\2\u037f\u0380\7\u011b\2\2\u0380")
        buf.write(u"\u00b5\3\2\2\2\u0381\u0382\7\u0116\2\2\u0382\u00b7\3")
        buf.write(u"\2\2\2\u0383\u0384\7\u0116\2\2\u0384\u00b9\3\2\2\2\u0385")
        buf.write(u"\u0386\b^\1\2\u0386\u0387\5\30\r\2\u0387\u038d\3\2\2")
        buf.write(u"\2\u0388\u0389\f\3\2\2\u0389\u038a\7\u00c3\2\2\u038a")
        buf.write(u"\u038c\5\30\r\2\u038b\u0388\3\2\2\2\u038c\u038f\3\2\2")
        buf.write(u"\2\u038d\u038b\3\2\2\2\u038d\u038e\3\2\2\2\u038e\u00bb")
        buf.write(u"\3\2\2\2\u038f\u038d\3\2\2\2\u0390\u039a\7\u011c\2\2")
        buf.write(u"\u0391\u0396\5\u00c0a\2\u0392\u0393\7\u011e\2\2\u0393")
        buf.write(u"\u0395\5\u00c0a\2\u0394\u0392\3\2\2\2\u0395\u0398\3\2")
        buf.write(u"\2\2\u0396\u0394\3\2\2\2\u0396\u0397\3\2\2\2\u0397\u039a")
        buf.write(u"\3\2\2\2\u0398\u0396\3\2\2\2\u0399\u0390\3\2\2\2\u0399")
        buf.write(u"\u0391\3\2\2\2\u039a\u00bd\3\2\2\2\u039b\u039d\7\u00e0")
        buf.write(u"\2\2\u039c\u039e\5\u00c8e\2\u039d\u039c\3\2\2\2\u039d")
        buf.write(u"\u039e\3\2\2\2\u039e\u03a0\3\2\2\2\u039f\u03a1\5\u00c6")
        buf.write(u"d\2\u03a0\u039f\3\2\2\2\u03a0\u03a1\3\2\2\2\u03a1\u03a2")
        buf.write(u"\3\2\2\2\u03a2\u03a3\5\u00bc_\2\u03a3\u03a4\5\u00dco")
        buf.write(u"\2\u03a4\u00bf\3\2\2\2\u03a5\u03ab\5J&\2\u03a6\u03a7")
        buf.write(u"\5\u00a8U\2\u03a7\u03a8\7\u0120\2\2\u03a8\u03a9\7\u011c")
        buf.write(u"\2\2\u03a9\u03ab\3\2\2\2\u03aa\u03a5\3\2\2\2\u03aa\u03a6")
        buf.write(u"\3\2\2\2\u03ab\u00c1\3\2\2\2\u03ac\u03ad\7Z\2\2\u03ad")
        buf.write(u"\u03ae\7\u011a\2\2\u03ae\u03af\7\u011c\2\2\u03af\u03b2")
        buf.write(u"\7\u011b\2\2\u03b0\u03b2\5\\/\2\u03b1\u03ac\3\2\2\2\u03b1")
        buf.write(u"\u03b0\3\2\2\2\u03b2\u00c3\3\2\2\2\u03b3\u03b4\t\6\2")
        buf.write(u"\2\u03b4\u00c5\3\2\2\2\u03b5\u03b6\7,\2\2\u03b6\u03b7")
        buf.write(u"\5\u00eav\2\u03b7\u00c7\3\2\2\2\u03b8\u03b9\t\7\2\2\u03b9")
        buf.write(u"\u00c9\3\2\2\2\u03ba\u03bb\t\b\2\2\u03bb\u00cb\3\2\2")
        buf.write(u"\2\u03bc\u03be\5\u00caf\2\u03bd\u03bc\3\2\2\2\u03bd\u03be")
        buf.write(u"\3\2\2\2\u03be\u03bf\3\2\2\2\u03bf\u03c0\5\u00eav\2\u03c0")
        buf.write(u"\u00cd\3\2\2\2\u03c1\u03c4\5(\25\2\u03c2\u03c4\5\u00ea")
        buf.write(u"v\2\u03c3\u03c1\3\2\2\2\u03c3\u03c2\3\2\2\2\u03c4\u00cf")
        buf.write(u"\3\2\2\2\u03c5\u03c7\5\u00ceh\2\u03c6\u03c8\5\u009aN")
        buf.write(u"\2\u03c7\u03c6\3\2\2\2\u03c7\u03c8\3\2\2\2\u03c8\u00d1")
        buf.write(u"\3\2\2\2\u03c9\u03ce\5\u00d0i\2\u03ca\u03cb\7\u011e\2")
        buf.write(u"\2\u03cb\u03cd\5\u00d0i\2\u03cc\u03ca\3\2\2\2\u03cd\u03d0")
        buf.write(u"\3\2\2\2\u03ce\u03cc\3\2\2\2\u03ce\u03cf\3\2\2\2\u03cf")
        buf.write(u"\u00d3\3\2\2\2\u03d0\u03ce\3\2\2\2\u03d1\u03d2\5T+\2")
        buf.write(u"\u03d2\u00d5\3\2\2\2\u03d3\u03d4\5$\23\2\u03d4\u00d7")
        buf.write(u"\3\2\2\2\u03d5\u03d8\5\u00d4k\2\u03d6\u03d8\5\u00f4{")
        buf.write(u"\2\u03d7\u03d5\3\2\2\2\u03d7\u03d6\3\2\2\2\u03d8\u00d9")
        buf.write(u"\3\2\2\2\u03d9\u03da\7\u011a\2\2\u03da\u03db\5\u00aa")
        buf.write(u"V\2\u03db\u03dc\7\u011b\2\2\u03dc\u00db\3\2\2\2\u03dd")
        buf.write(u"\u03df\5X-\2\u03de\u03e0\5\u00fe\u0080\2\u03df\u03de")
        buf.write(u"\3\2\2\2\u03df\u03e0\3\2\2\2\u03e0\u03e2\3\2\2\2\u03e1")
        buf.write(u"\u03e3\5`\61\2\u03e2\u03e1\3\2\2\2\u03e2\u03e3\3\2\2")
        buf.write(u"\2\u03e3\u03e5\3\2\2\2\u03e4\u03e6\5f\64\2\u03e5\u03e4")
        buf.write(u"\3\2\2\2\u03e5\u03e6\3\2\2\2\u03e6\u03e8\3\2\2\2\u03e7")
        buf.write(u"\u03e9\5\u0098M\2\u03e8\u03e7\3\2\2\2\u03e8\u03e9\3\2")
        buf.write(u"\2\2\u03e9\u03eb\3\2\2\2\u03ea\u03ec\5\u0096L\2\u03eb")
        buf.write(u"\u03ea\3\2\2\2\u03eb\u03ec\3\2\2\2\u03ec\u00dd\3\2\2")
        buf.write(u"\2\u03ed\u03ee\5\u00b8]\2\u03ee\u03ef\7\u0120\2\2\u03ef")
        buf.write(u"\u03f1\3\2\2\2\u03f0\u03ed\3\2\2\2\u03f0\u03f1\3\2\2")
        buf.write(u"\2\u03f1\u03f2\3\2\2\2\u03f2\u03f3\5h\65\2\u03f3\u00df")
        buf.write(u"\3\2\2\2\u03f4\u03f5\bq\1\2\u03f5\u03f7\5\u00dep\2\u03f6")
        buf.write(u"\u03f8\5F$\2\u03f7\u03f6\3\2\2\2\u03f7\u03f8\3\2\2\2")
        buf.write(u"\u03f8\u0401\3\2\2\2\u03f9\u03fa\5L\'\2\u03fa\u03fb\5")
        buf.write(u"F$\2\u03fb\u0401\3\2\2\2\u03fc\u03fd\7\u011a\2\2\u03fd")
        buf.write(u"\u03fe\5z>\2\u03fe\u03ff\7\u011b\2\2\u03ff\u0401\3\2")
        buf.write(u"\2\2\u0400\u03f4\3\2\2\2\u0400\u03f9\3\2\2\2\u0400\u03fc")
        buf.write(u"\3\2\2\2\u0401\u0410\3\2\2\2\u0402\u0404\f\4\2\2\u0403")
        buf.write(u"\u0405\7\u00b4\2\2\u0404\u0403\3\2\2\2\u0404\u0405\3")
        buf.write(u"\2\2\2\u0405\u0407\3\2\2\2\u0406\u0408\5x=\2\u0407\u0406")
        buf.write(u"\3\2\2\2\u0407\u0408\3\2\2\2\u0408\u0409\3\2\2\2\u0409")
        buf.write(u"\u040a\7\u00a2\2\2\u040a\u040c\5\u00e0q\2\u040b\u040d")
        buf.write(u"\5v<\2\u040c\u040b\3\2\2\2\u040c\u040d\3\2\2\2\u040d")
        buf.write(u"\u040f\3\2\2\2\u040e\u0402\3\2\2\2\u040f\u0412\3\2\2")
        buf.write(u"\2\u0410\u040e\3\2\2\2\u0410\u0411\3\2\2\2\u0411\u00e1")
        buf.write(u"\3\2\2\2\u0412\u0410\3\2\2\2\u0413\u0414\5\u00dan\2\u0414")
        buf.write(u"\u00e3\3\2\2\2\u0415\u0416\bs\1\2\u0416\u0417\5V,\2\u0417")
        buf.write(u"\u0423\3\2\2\2\u0418\u0419\f\5\2\2\u0419\u041a\7\u011c")
        buf.write(u"\2\2\u041a\u0422\5V,\2\u041b\u041c\f\4\2\2\u041c\u041d")
        buf.write(u"\7\u0129\2\2\u041d\u0422\5V,\2\u041e\u041f\f\3\2\2\u041f")
        buf.write(u"\u0420\7\u0130\2\2\u0420\u0422\5V,\2\u0421\u0418\3\2")
        buf.write(u"\2\2\u0421\u041b\3\2\2\2\u0421\u041e\3\2\2\2\u0422\u0425")
        buf.write(u"\3\2\2\2\u0423\u0421\3\2\2\2\u0423\u0424\3\2\2\2\u0424")
        buf.write(u"\u00e5\3\2\2\2\u0425\u0423\3\2\2\2\u0426\u0427\7\4\2")
        buf.write(u"\2\u0427\u0428\7\u011a\2\2\u0428\u0429\5\u0092J\2\u0429")
        buf.write(u"\u042a\7\u011b\2\2\u042a\u0456\3\2\2\2\u042b\u042c\7")
        buf.write(u"\4\2\2\u042c\u042d\7\u011a\2\2\u042d\u042e\5\u0092J\2")
        buf.write(u"\u042e\u042f\7\u011b\2\2\u042f\u0456\3\2\2\2\u0430\u0431")
        buf.write(u"\7\6\2\2\u0431\u0432\7\u011a\2\2\u0432\u0433\5\u0092")
        buf.write(u"J\2\u0433\u0434\7\u011b\2\2\u0434\u0456\3\2\2\2\u0435")
        buf.write(u"\u0436\7\7\2\2\u0436\u0437\7\u011a\2\2\u0437\u0438\5")
        buf.write(u"\u0092J\2\u0438\u0439\7\u011b\2\2\u0439\u0456\3\2\2\2")
        buf.write(u"\u043a\u043b\7\b\2\2\u043b\u043c\7\u011a\2\2\u043c\u043d")
        buf.write(u"\5\u0092J\2\u043d\u043e\7\u011e\2\2\u043e\u043f\5\u0092")
        buf.write(u"J\2\u043f\u0440\7\u011b\2\2\u0440\u0456\3\2\2\2\u0441")
        buf.write(u"\u0442\7\25\2\2\u0442\u0443\7\u011a\2\2\u0443\u0444\5")
        buf.write(u"\u0092J\2\u0444\u0445\7\u011b\2\2\u0445\u0456\3\2\2\2")
        buf.write(u"\u0446\u0447\7\26\2\2\u0447\u0448\7\u011a\2\2\u0448\u0449")
        buf.write(u"\5\u0092J\2\u0449\u044a\7\u011b\2\2\u044a\u0456\3\2\2")
        buf.write(u"\2\u044b\u044c\7)\2\2\u044c\u044d\7\u011a\2\2\u044d\u044e")
        buf.write(u"\5\u0092J\2\u044e\u044f\7\u011b\2\2\u044f\u0456\3\2\2")
        buf.write(u"\2\u0450\u0451\7+\2\2\u0451\u0452\7\u011a\2\2\u0452\u0453")
        buf.write(u"\5\u0092J\2\u0453\u0454\7\u011b\2\2\u0454\u0456\3\2\2")
        buf.write(u"\2\u0455\u0426\3\2\2\2\u0455\u042b\3\2\2\2\u0455\u0430")
        buf.write(u"\3\2\2\2\u0455\u0435\3\2\2\2\u0455\u043a\3\2\2\2\u0455")
        buf.write(u"\u0441\3\2\2\2\u0455\u0446\3\2\2\2\u0455\u044b\3\2\2")
        buf.write(u"\2\u0455\u0450\3\2\2\2\u0456\u00e7\3\2\2\2\u0457\u0458")
        buf.write(u"\7\u0116\2\2\u0458\u00e9\3\2\2\2\u0459\u045a\7\u0112")
        buf.write(u"\2\2\u045a\u00eb\3\2\2\2\u045b\u045c\7\u0115\2\2\u045c")
        buf.write(u"\u00ed\3\2\2\2\u045d\u0460\5\u00f0y\2\u045e\u0460\5Z")
        buf.write(u".\2\u045f\u045d\3\2\2\2\u045f\u045e\3\2\2\2\u0460\u00ef")
        buf.write(u"\3\2\2\2\u0461\u0465\5P)\2\u0462\u0465\5\2\2\2\u0463")
        buf.write(u"\u0465\5\u00ecw\2\u0464\u0461\3\2\2\2\u0464\u0462\3\2")
        buf.write(u"\2\2\u0464\u0463\3\2\2\2\u0465\u00f1\3\2\2\2\u0466\u0467")
        buf.write(u"\5\u00eex\2\u0467\u00f3\3\2\2\2\u0468\u0469\5\u00f6|")
        buf.write(u"\2\u0469\u0472\7\u011a\2\2\u046a\u046f\5\u00f8}\2\u046b")
        buf.write(u"\u046c\7\u011e\2\2\u046c\u046e\5\u00f8}\2\u046d\u046b")
        buf.write(u"\3\2\2\2\u046e\u0471\3\2\2\2\u046f\u046d\3\2\2\2\u046f")
        buf.write(u"\u0470\3\2\2\2\u0470\u0473\3\2\2\2\u0471\u046f\3\2\2")
        buf.write(u"\2\u0472\u046a\3\2\2\2\u0472\u0473\3\2\2\2\u0473\u0474")
        buf.write(u"\3\2\2\2\u0474\u0475\7\u011b\2\2\u0475\u00f5\3\2\2\2")
        buf.write(u"\u0476\u0477\5\u00b6\\\2\u0477\u00f7\3\2\2\2\u0478\u0479")
        buf.write(u"\5\u00fa~\2\u0479\u00f9\3\2\2\2\u047a\u047f\5\u0092J")
        buf.write(u"\2\u047b\u047f\5\u00d6l\2\u047c\u047f\5\32\16\2\u047d")
        buf.write(u"\u047f\5^\60\2\u047e\u047a\3\2\2\2\u047e\u047b\3\2\2")
        buf.write(u"\2\u047e\u047c\3\2\2\2\u047e\u047d\3\2\2\2\u047f\u00fb")
        buf.write(u"\3\2\2\2\u0480\u0488\5\u00f2z\2\u0481\u0488\5,\27\2\u0482")
        buf.write(u"\u0488\5\u00c2b\2\u0483\u0484\7\u011a\2\2\u0484\u0485")
        buf.write(u"\5\u00fa~\2\u0485\u0486\7\u011b\2\2\u0486\u0488\3\2\2")
        buf.write(u"\2\u0487\u0480\3\2\2\2\u0487\u0481\3\2\2\2\u0487\u0482")
        buf.write(u"\3\2\2\2\u0487\u0483\3\2\2\2\u0488\u00fd\3\2\2\2\u0489")
        buf.write(u"\u048a\7\u010c\2\2\u048a\u048b\5\u00ba^\2\u048b\u00ff")
        buf.write(u"\3\2\2\2\u048c\u0498\5\u00acW\2\u048d\u048e\7\u011a\2")
        buf.write(u"\2\u048e\u0493\5(\25\2\u048f\u0490\7\u011e\2\2\u0490")
        buf.write(u"\u0492\5(\25\2\u0491\u048f\3\2\2\2\u0492\u0495\3\2\2")
        buf.write(u"\2\u0493\u0491\3\2\2\2\u0493\u0494\3\2\2\2\u0494\u0496")
        buf.write(u"\3\2\2\2\u0495\u0493\3\2\2\2\u0496\u0497\7\u011b\2\2")
        buf.write(u"\u0497\u0499\3\2\2\2\u0498\u048d\3\2\2\2\u0498\u0499")
        buf.write(u"\3\2\2\2\u0499\u049a\3\2\2\2\u049a\u049b\7\67\2\2\u049b")
        buf.write(u"\u049d\7\u011a\2\2\u049c\u049e\5\u00aeX\2\u049d\u049c")
        buf.write(u"\3\2\2\2\u049d\u049e\3\2\2\2\u049e\u049f\3\2\2\2\u049f")
        buf.write(u"\u04a0\7\u011b\2\2\u04a0\u0101\3\2\2\2k\u010a\u0110\u0120")
        buf.write(u"\u012c\u0136\u013b\u0153\u015b\u0161\u0165\u0178\u017e")
        buf.write(u"\u0195\u01ac\u01b6\u01c8\u01cf\u01d1\u01d5\u01e0\u01ea")
        buf.write(u"\u01f2\u01fe\u020b\u0213\u0217\u0221\u0228\u0238\u023d")
        buf.write(u"\u023f\u0243\u0246\u024b\u0251\u0255\u025c\u0261\u02a1")
        buf.write(u"\u02ae\u02b2\u02bd\u02c4\u02c8\u02cf\u02d5\u02d9\u02df")
        buf.write(u"\u02e4\u02ea\u02ed\u02f1\u02f8\u030c\u030e\u0315\u0336")
        buf.write(u"\u0340\u0344\u0349\u034e\u0353\u0359\u035c\u035e\u0365")
        buf.write(u"\u036d\u0372\u0377\u038d\u0396\u0399\u039d\u03a0\u03aa")
        buf.write(u"\u03b1\u03bd\u03c3\u03c7\u03ce\u03d7\u03df\u03e2\u03e5")
        buf.write(u"\u03e8\u03eb\u03f0\u03f7\u0400\u0404\u0407\u040c\u0410")
        buf.write(u"\u0421\u0423\u0455\u045f\u0464\u046f\u0472\u047e\u0487")
        buf.write(u"\u0493\u0498\u049d")
        return buf.getvalue()


class ADQLParser ( Parser ):

    grammarFileName = "ADQLParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"'&'", u"'~'", u"'^'", u"'('", u"')'", 
                     u"'*'", u"'+'", u"','", u"'-'", u"'.'", u"':'", u"';'", 
                     u"'<'", u"'='", u"'>'", u"'?'", u"'|'", u"'_'", u"'/'", 
                     u"'||'", u"'<='", u"'>='", u"<INVALID>", u"'\"'", u"'''", 
                     u"'%'" ]

    symbolicNames = [ u"<INVALID>", u"ABS", u"ACOS", u"AREA", u"ASIN", u"ATAN", 
                      u"ATAN2", u"BIT_AND", u"BIT_NOT", u"BIT_OR", u"BIT_XOR", 
                      u"BOX", u"CEILING", u"CENTROID", u"CIRCLE", u"CONTAINS", 
                      u"COORD1", u"COORD2", u"COORDSYS", u"COS", u"COT", 
                      u"DEGREES", u"DISTANCE", u"EXP", u"FLOOR", u"ILIKE", 
                      u"INTERSECTS", u"IN_UNIT", u"LOG", u"LOG10", u"MOD", 
                      u"PI", u"POINT", u"POLYGON", u"POWER", u"RADIANS", 
                      u"REGION", u"RAND", u"ROUND", u"SIN", u"SQRT", u"TAN", 
                      u"TOP", u"TRUNCATE", u"ABSOLUTE", u"ACTION", u"ADD", 
                      u"ALL", u"ALLOCATE", u"ALTER", u"AND", u"ANY", u"ARE", 
                      u"AS", u"ASC", u"ASSERTION", u"AT", u"AUTHORIZATION", 
                      u"AVG", u"BEGIN", u"BETWEEN", u"BIT", u"BIT_LENGTH", 
                      u"BOTH", u"BY", u"CASCADE", u"CASCADED", u"CASE", 
                      u"CAST", u"CATALOG", u"CHAR", u"CHARACTER", u"CHAR_LENGTH", 
                      u"CHARACTER_LENGTH", u"CHECK", u"CLOSE", u"COALESCE", 
                      u"COLLATE", u"COLLATION", u"COLUMN", u"COMMIT", u"CONNECT", 
                      u"CONNECTION", u"CONSTRAINT", u"CONSTRAINTS", u"CONTINUE", 
                      u"CONVERT", u"CORRESPONDING", u"COUNT", u"CREATE", 
                      u"CROSS", u"CURRENT", u"CURRENT_DATE", u"CURRENT_TIME", 
                      u"CURRENT_TIMESTAMP", u"CURRENT_USER", u"CURSOR", 
                      u"DATE", u"DAY", u"DEALLOCATE", u"DECIMAL", u"DECLARE", 
                      u"DEFAULT", u"DEFERRABLE", u"DEFERRED", u"DELETE", 
                      u"DESC", u"DESCRIBE", u"DESCRIPTOR", u"DIAGNOSTICS", 
                      u"DISCONNECT", u"DISTINCT", u"DOMAIN", u"DOUBLE", 
                      u"DROP", u"E_SYM", u"ELSE", u"END", u"ENDEXEC_SYM", 
                      u"ESCAPE", u"EXCEPT", u"EXCEPTION", u"EXEC", u"EXECUTE", 
                      u"EXISTS", u"EXTERNAL", u"EXTRACT", u"FALSE", u"FETCH", 
                      u"FIRST", u"FLOAT", u"FOR", u"FOREIGN", u"FOUND", 
                      u"FROM", u"FULL", u"GET", u"GLOBAL", u"GO", u"GOTO", 
                      u"GRANT", u"GROUP", u"HAVING", u"HOUR", u"IDENTITY", 
                      u"IMMEDIATE", u"IN", u"INDICATOR", u"INITIALLY", u"INNER", 
                      u"INPUT", u"INSENSITIVE", u"INSERT", u"INT_SYM", u"INTEGER", 
                      u"INTERSECT", u"INTERVAL", u"INTO", u"IS", u"ISOLATION", 
                      u"JOIN", u"KEY", u"LANGUAGE", u"LAST", u"LEADING", 
                      u"LEFT", u"LEVEL", u"LIKE", u"LOCAL", u"LOWER", u"MATCH", 
                      u"MAX", u"MIN", u"MINUTE", u"MODULE", u"MONTH", u"NAMES", 
                      u"NATIONAL", u"NATURAL", u"NCHAR", u"NEXT", u"NO", 
                      u"NOT", u"NULL", u"NULLIF", u"NUMERIC", u"OCTET_LENGTH", 
                      u"OF", u"OFFSET", u"ON", u"ONLY", u"OPEN", u"OPTION", 
                      u"OR", u"ORDER", u"OUTER", u"OUTPUT", u"OVERLAPS", 
                      u"PAD", u"PARTIAL", u"POSITION", u"PRECISION", u"PREPARE", 
                      u"PRESERVE", u"PRIMARY", u"PRIOR", u"PRIVILEGES", 
                      u"PROCEDURE", u"PUBLIC", u"READ", u"REAL_SYM", u"REFERENCES", 
                      u"RELATIVE", u"RESTRICT", u"REVOKE", u"RIGHT", u"ROLLBACK", 
                      u"ROWS", u"SCHEMA", u"SCROLL", u"SECOND", u"SECTION", 
                      u"SELECT", u"SESSION", u"SESSION_USER", u"SET", u"SIZE", 
                      u"SMALLINT", u"SOME", u"SPACE", u"SQL", u"SQLCODE", 
                      u"SQLERROR", u"SQLSTATE", u"SUBSTRING", u"SUM", u"SYSTEM_USER", 
                      u"TABLE", u"TEMPORARY", u"THEN", u"TIME", u"TIMESTAMP", 
                      u"TIMEZONE_HOUR", u"TIMEZONE_MINUTE", u"TO", u"TRAILING", 
                      u"TRANSACTION", u"TRANSLATE", u"TRANSLATION", u"TRIM", 
                      u"TRUE", u"UNION", u"UNIQUE", u"UNKNOWN", u"UPDATE", 
                      u"UPPER", u"USAGE", u"USER", u"USING", u"VALUE", u"VALUES", 
                      u"VARCHAR", u"VARYING", u"VIEW", u"WHEN", u"WHENEVER", 
                      u"WHERE", u"WITH", u"WORK", u"WRITE", u"YEAR", u"ZONE", 
                      u"INT", u"EXPONENT", u"REAL", u"HEX_DIGIT", u"ID", 
                      u"AMPERSAND", u"TILDE", u"CIRCUMFLEX", u"LPAREN", 
                      u"RPAREN", u"ASTERISK", u"PLUS", u"COMMA", u"MINUS", 
                      u"DOT", u"COLON", u"SEMI", u"LTH", u"EQ", u"GTH", 
                      u"QUESTION", u"VERTBAR", u"UNDERSCORE", u"SOLIDUS", 
                      u"CONCAT", u"LEET", u"GRET", u"NOT_EQ", u"DQ", u"SQ", 
                      u"MOD_SYM", u"DQ_SYM", u"WS" ]

    RULE_approximate_numeric_literal = 0
    RULE_area = 1
    RULE_as_clause = 2
    RULE_between_predicate = 3
    RULE_bitwise_and = 4
    RULE_bitwise_not = 5
    RULE_bitwise_or = 6
    RULE_bitwise_xor = 7
    RULE_boolean_factor = 8
    RULE_boolean_literal = 9
    RULE_boolean_primary = 10
    RULE_boolean_term = 11
    RULE_boolean_value_expression = 12
    RULE_box = 13
    RULE_catalog_name = 14
    RULE_centroid = 15
    RULE_character_string_literal = 16
    RULE_character_value_expression = 17
    RULE_circle = 18
    RULE_column_name = 19
    RULE_column_name_list = 20
    RULE_column_reference = 21
    RULE_comp_op = 22
    RULE_comparison_predicate = 23
    RULE_concatenation_operator = 24
    RULE_contains = 25
    RULE_coord_sys = 26
    RULE_coord_value = 27
    RULE_coord1 = 28
    RULE_coord2 = 29
    RULE_coordinate1 = 30
    RULE_coordinate2 = 31
    RULE_coordinates = 32
    RULE_correlation_name = 33
    RULE_correlation_specification = 34
    RULE_delimited_identifier = 35
    RULE_derived_column = 36
    RULE_derived_table = 37
    RULE_distance = 38
    RULE_exact_numeric_literal = 39
    RULE_exists_predicate = 40
    RULE_extract_coordsys = 41
    RULE_factor = 42
    RULE_from_clause = 43
    RULE_general_literal = 44
    RULE_general_set_function = 45
    RULE_geometry_value_expression = 46
    RULE_group_by_clause = 47
    RULE_grouping_column_reference = 48
    RULE_grouping_column_reference_list = 49
    RULE_having_clause = 50
    RULE_identifier = 51
    RULE_in_predicate = 52
    RULE_in_predicate_value = 53
    RULE_in_value_list = 54
    RULE_intersects = 55
    RULE_join_column_list = 56
    RULE_join_condition = 57
    RULE_join_specification = 58
    RULE_join_type = 59
    RULE_joined_table = 60
    RULE_like_predicate = 61
    RULE_match_value = 62
    RULE_math_function = 63
    RULE_named_columns_join = 64
    RULE_non_join_query_expression = 65
    RULE_non_join_query_primary = 66
    RULE_non_join_query_term = 67
    RULE_non_predicate_geometry_function = 68
    RULE_null_predicate = 69
    RULE_numeric_geometry_function = 70
    RULE_numeric_primary = 71
    RULE_numeric_value_expression = 72
    RULE_numeric_value_function = 73
    RULE_offset_clause = 74
    RULE_order_by_clause = 75
    RULE_ordering_specification = 76
    RULE_outer_join_type = 77
    RULE_pattern = 78
    RULE_point = 79
    RULE_polygon = 80
    RULE_predicate = 81
    RULE_predicate_geometry_function = 82
    RULE_qualifier = 83
    RULE_query_expression = 84
    RULE_query_name = 85
    RULE_query_specification = 86
    RULE_query_term = 87
    RULE_radius = 88
    RULE_region = 89
    RULE_regular_identifier = 90
    RULE_schema_name = 91
    RULE_search_condition = 92
    RULE_select_list = 93
    RULE_select_query = 94
    RULE_select_sublist = 95
    RULE_set_function_specification = 96
    RULE_set_function_type = 97
    RULE_set_limit = 98
    RULE_set_quantifier = 99
    RULE_sign = 100
    RULE_signed_integer = 101
    RULE_sort_key = 102
    RULE_sort_specification = 103
    RULE_sort_specification_list = 104
    RULE_string_geometry_function = 105
    RULE_string_value_expression = 106
    RULE_string_value_function = 107
    RULE_subquery = 108
    RULE_table_expression = 109
    RULE_table_name = 110
    RULE_table_reference = 111
    RULE_table_subquery = 112
    RULE_term = 113
    RULE_trig_function = 114
    RULE_unqualified_schema_name = 115
    RULE_unsigned_decimal = 116
    RULE_unsigned_hexadecimal = 117
    RULE_unsigned_literal = 118
    RULE_unsigned_numeric_literal = 119
    RULE_unsigned_value_specification = 120
    RULE_user_defined_function = 121
    RULE_user_defined_function_name = 122
    RULE_user_defined_function_param = 123
    RULE_value_expression = 124
    RULE_value_expression_primary = 125
    RULE_where_clause = 126
    RULE_with_query = 127

    ruleNames =  [ u"approximate_numeric_literal", u"area", u"as_clause", 
                   u"between_predicate", u"bitwise_and", u"bitwise_not", 
                   u"bitwise_or", u"bitwise_xor", u"boolean_factor", u"boolean_literal", 
                   u"boolean_primary", u"boolean_term", u"boolean_value_expression", 
                   u"box", u"catalog_name", u"centroid", u"character_string_literal", 
                   u"character_value_expression", u"circle", u"column_name", 
                   u"column_name_list", u"column_reference", u"comp_op", 
                   u"comparison_predicate", u"concatenation_operator", u"contains", 
                   u"coord_sys", u"coord_value", u"coord1", u"coord2", u"coordinate1", 
                   u"coordinate2", u"coordinates", u"correlation_name", 
                   u"correlation_specification", u"delimited_identifier", 
                   u"derived_column", u"derived_table", u"distance", u"exact_numeric_literal", 
                   u"exists_predicate", u"extract_coordsys", u"factor", 
                   u"from_clause", u"general_literal", u"general_set_function", 
                   u"geometry_value_expression", u"group_by_clause", u"grouping_column_reference", 
                   u"grouping_column_reference_list", u"having_clause", 
                   u"identifier", u"in_predicate", u"in_predicate_value", 
                   u"in_value_list", u"intersects", u"join_column_list", 
                   u"join_condition", u"join_specification", u"join_type", 
                   u"joined_table", u"like_predicate", u"match_value", u"math_function", 
                   u"named_columns_join", u"non_join_query_expression", 
                   u"non_join_query_primary", u"non_join_query_term", u"non_predicate_geometry_function", 
                   u"null_predicate", u"numeric_geometry_function", u"numeric_primary", 
                   u"numeric_value_expression", u"numeric_value_function", 
                   u"offset_clause", u"order_by_clause", u"ordering_specification", 
                   u"outer_join_type", u"pattern", u"point", u"polygon", 
                   u"predicate", u"predicate_geometry_function", u"qualifier", 
                   u"query_expression", u"query_name", u"query_specification", 
                   u"query_term", u"radius", u"region", u"regular_identifier", 
                   u"schema_name", u"search_condition", u"select_list", 
                   u"select_query", u"select_sublist", u"set_function_specification", 
                   u"set_function_type", u"set_limit", u"set_quantifier", 
                   u"sign", u"signed_integer", u"sort_key", u"sort_specification", 
                   u"sort_specification_list", u"string_geometry_function", 
                   u"string_value_expression", u"string_value_function", 
                   u"subquery", u"table_expression", u"table_name", u"table_reference", 
                   u"table_subquery", u"term", u"trig_function", u"unqualified_schema_name", 
                   u"unsigned_decimal", u"unsigned_hexadecimal", u"unsigned_literal", 
                   u"unsigned_numeric_literal", u"unsigned_value_specification", 
                   u"user_defined_function", u"user_defined_function_name", 
                   u"user_defined_function_param", u"value_expression", 
                   u"value_expression_primary", u"where_clause", u"with_query" ]

    EOF = Token.EOF
    ABS=1
    ACOS=2
    AREA=3
    ASIN=4
    ATAN=5
    ATAN2=6
    BIT_AND=7
    BIT_NOT=8
    BIT_OR=9
    BIT_XOR=10
    BOX=11
    CEILING=12
    CENTROID=13
    CIRCLE=14
    CONTAINS=15
    COORD1=16
    COORD2=17
    COORDSYS=18
    COS=19
    COT=20
    DEGREES=21
    DISTANCE=22
    EXP=23
    FLOOR=24
    ILIKE=25
    INTERSECTS=26
    IN_UNIT=27
    LOG=28
    LOG10=29
    MOD=30
    PI=31
    POINT=32
    POLYGON=33
    POWER=34
    RADIANS=35
    REGION=36
    RAND=37
    ROUND=38
    SIN=39
    SQRT=40
    TAN=41
    TOP=42
    TRUNCATE=43
    ABSOLUTE=44
    ACTION=45
    ADD=46
    ALL=47
    ALLOCATE=48
    ALTER=49
    AND=50
    ANY=51
    ARE=52
    AS=53
    ASC=54
    ASSERTION=55
    AT=56
    AUTHORIZATION=57
    AVG=58
    BEGIN=59
    BETWEEN=60
    BIT=61
    BIT_LENGTH=62
    BOTH=63
    BY=64
    CASCADE=65
    CASCADED=66
    CASE=67
    CAST=68
    CATALOG=69
    CHAR=70
    CHARACTER=71
    CHAR_LENGTH=72
    CHARACTER_LENGTH=73
    CHECK=74
    CLOSE=75
    COALESCE=76
    COLLATE=77
    COLLATION=78
    COLUMN=79
    COMMIT=80
    CONNECT=81
    CONNECTION=82
    CONSTRAINT=83
    CONSTRAINTS=84
    CONTINUE=85
    CONVERT=86
    CORRESPONDING=87
    COUNT=88
    CREATE=89
    CROSS=90
    CURRENT=91
    CURRENT_DATE=92
    CURRENT_TIME=93
    CURRENT_TIMESTAMP=94
    CURRENT_USER=95
    CURSOR=96
    DATE=97
    DAY=98
    DEALLOCATE=99
    DECIMAL=100
    DECLARE=101
    DEFAULT=102
    DEFERRABLE=103
    DEFERRED=104
    DELETE=105
    DESC=106
    DESCRIBE=107
    DESCRIPTOR=108
    DIAGNOSTICS=109
    DISCONNECT=110
    DISTINCT=111
    DOMAIN=112
    DOUBLE=113
    DROP=114
    E_SYM=115
    ELSE=116
    END=117
    ENDEXEC_SYM=118
    ESCAPE=119
    EXCEPT=120
    EXCEPTION=121
    EXEC=122
    EXECUTE=123
    EXISTS=124
    EXTERNAL=125
    EXTRACT=126
    FALSE=127
    FETCH=128
    FIRST=129
    FLOAT=130
    FOR=131
    FOREIGN=132
    FOUND=133
    FROM=134
    FULL=135
    GET=136
    GLOBAL=137
    GO=138
    GOTO=139
    GRANT=140
    GROUP=141
    HAVING=142
    HOUR=143
    IDENTITY=144
    IMMEDIATE=145
    IN=146
    INDICATOR=147
    INITIALLY=148
    INNER=149
    INPUT=150
    INSENSITIVE=151
    INSERT=152
    INT_SYM=153
    INTEGER=154
    INTERSECT=155
    INTERVAL=156
    INTO=157
    IS=158
    ISOLATION=159
    JOIN=160
    KEY=161
    LANGUAGE=162
    LAST=163
    LEADING=164
    LEFT=165
    LEVEL=166
    LIKE=167
    LOCAL=168
    LOWER=169
    MATCH=170
    MAX=171
    MIN=172
    MINUTE=173
    MODULE=174
    MONTH=175
    NAMES=176
    NATIONAL=177
    NATURAL=178
    NCHAR=179
    NEXT=180
    NO=181
    NOT=182
    NULL=183
    NULLIF=184
    NUMERIC=185
    OCTET_LENGTH=186
    OF=187
    OFFSET=188
    ON=189
    ONLY=190
    OPEN=191
    OPTION=192
    OR=193
    ORDER=194
    OUTER=195
    OUTPUT=196
    OVERLAPS=197
    PAD=198
    PARTIAL=199
    POSITION=200
    PRECISION=201
    PREPARE=202
    PRESERVE=203
    PRIMARY=204
    PRIOR=205
    PRIVILEGES=206
    PROCEDURE=207
    PUBLIC=208
    READ=209
    REAL_SYM=210
    REFERENCES=211
    RELATIVE=212
    RESTRICT=213
    REVOKE=214
    RIGHT=215
    ROLLBACK=216
    ROWS=217
    SCHEMA=218
    SCROLL=219
    SECOND=220
    SECTION=221
    SELECT=222
    SESSION=223
    SESSION_USER=224
    SET=225
    SIZE=226
    SMALLINT=227
    SOME=228
    SPACE=229
    SQL=230
    SQLCODE=231
    SQLERROR=232
    SQLSTATE=233
    SUBSTRING=234
    SUM=235
    SYSTEM_USER=236
    TABLE=237
    TEMPORARY=238
    THEN=239
    TIME=240
    TIMESTAMP=241
    TIMEZONE_HOUR=242
    TIMEZONE_MINUTE=243
    TO=244
    TRAILING=245
    TRANSACTION=246
    TRANSLATE=247
    TRANSLATION=248
    TRIM=249
    TRUE=250
    UNION=251
    UNIQUE=252
    UNKNOWN=253
    UPDATE=254
    UPPER=255
    USAGE=256
    USER=257
    USING=258
    VALUE=259
    VALUES=260
    VARCHAR=261
    VARYING=262
    VIEW=263
    WHEN=264
    WHENEVER=265
    WHERE=266
    WITH=267
    WORK=268
    WRITE=269
    YEAR=270
    ZONE=271
    INT=272
    EXPONENT=273
    REAL=274
    HEX_DIGIT=275
    ID=276
    AMPERSAND=277
    TILDE=278
    CIRCUMFLEX=279
    LPAREN=280
    RPAREN=281
    ASTERISK=282
    PLUS=283
    COMMA=284
    MINUS=285
    DOT=286
    COLON=287
    SEMI=288
    LTH=289
    EQ=290
    GTH=291
    QUESTION=292
    VERTBAR=293
    UNDERSCORE=294
    SOLIDUS=295
    CONCAT=296
    LEET=297
    GRET=298
    NOT_EQ=299
    DQ=300
    SQ=301
    MOD_SYM=302
    DQ_SYM=303
    WS=304

    def __init__(self, input, output=sys.stdout):
        super(ADQLParser, self).__init__(input, output=output)
        self.checkVersion("4.7")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class Approximate_numeric_literalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Approximate_numeric_literalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def REAL(self):
            return self.getToken(ADQLParser.REAL, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_approximate_numeric_literal

        def enterRule(self, listener):
            if hasattr(listener, "enterApproximate_numeric_literal"):
                listener.enterApproximate_numeric_literal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitApproximate_numeric_literal"):
                listener.exitApproximate_numeric_literal(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitApproximate_numeric_literal"):
                return visitor.visitApproximate_numeric_literal(self)
            else:
                return visitor.visitChildren(self)




    def approximate_numeric_literal(self):

        localctx = ADQLParser.Approximate_numeric_literalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_approximate_numeric_literal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 256
            self.match(ADQLParser.REAL)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AreaContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.AreaContext, self).__init__(parent, invokingState)
            self.parser = parser

        def AREA(self):
            return self.getToken(ADQLParser.AREA, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def geometry_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Geometry_value_expressionContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_area

        def enterRule(self, listener):
            if hasattr(listener, "enterArea"):
                listener.enterArea(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitArea"):
                listener.exitArea(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitArea"):
                return visitor.visitArea(self)
            else:
                return visitor.visitChildren(self)




    def area(self):

        localctx = ADQLParser.AreaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_area)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 258
            self.match(ADQLParser.AREA)
            self.state = 259
            self.match(ADQLParser.LPAREN)
            self.state = 260
            self.geometry_value_expression()
            self.state = 261
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class As_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.As_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def column_name(self):
            return self.getTypedRuleContext(ADQLParser.Column_nameContext,0)


        def AS(self):
            return self.getToken(ADQLParser.AS, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_as_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterAs_clause"):
                listener.enterAs_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitAs_clause"):
                listener.exitAs_clause(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitAs_clause"):
                return visitor.visitAs_clause(self)
            else:
                return visitor.visitChildren(self)




    def as_clause(self):

        localctx = ADQLParser.As_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_as_clause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 264
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.AS:
                self.state = 263
                self.match(ADQLParser.AS)


            self.state = 266
            self.column_name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Between_predicateContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Between_predicateContext, self).__init__(parent, invokingState)
            self.parser = parser

        def value_expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Value_expressionContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Value_expressionContext,i)


        def BETWEEN(self):
            return self.getToken(ADQLParser.BETWEEN, 0)

        def AND(self):
            return self.getToken(ADQLParser.AND, 0)

        def NOT(self):
            return self.getToken(ADQLParser.NOT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_between_predicate

        def enterRule(self, listener):
            if hasattr(listener, "enterBetween_predicate"):
                listener.enterBetween_predicate(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBetween_predicate"):
                listener.exitBetween_predicate(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitBetween_predicate"):
                return visitor.visitBetween_predicate(self)
            else:
                return visitor.visitChildren(self)




    def between_predicate(self):

        localctx = ADQLParser.Between_predicateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_between_predicate)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 268
            self.value_expression()
            self.state = 270
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.NOT:
                self.state = 269
                self.match(ADQLParser.NOT)


            self.state = 272
            self.match(ADQLParser.BETWEEN)
            self.state = 273
            self.value_expression()
            self.state = 274
            self.match(ADQLParser.AND)
            self.state = 275
            self.value_expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Bitwise_andContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Bitwise_andContext, self).__init__(parent, invokingState)
            self.parser = parser

        def AMPERSAND(self):
            return self.getToken(ADQLParser.AMPERSAND, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_bitwise_and

        def enterRule(self, listener):
            if hasattr(listener, "enterBitwise_and"):
                listener.enterBitwise_and(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBitwise_and"):
                listener.exitBitwise_and(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitBitwise_and"):
                return visitor.visitBitwise_and(self)
            else:
                return visitor.visitChildren(self)




    def bitwise_and(self):

        localctx = ADQLParser.Bitwise_andContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_bitwise_and)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 277
            self.match(ADQLParser.AMPERSAND)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Bitwise_notContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Bitwise_notContext, self).__init__(parent, invokingState)
            self.parser = parser

        def TILDE(self):
            return self.getToken(ADQLParser.TILDE, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_bitwise_not

        def enterRule(self, listener):
            if hasattr(listener, "enterBitwise_not"):
                listener.enterBitwise_not(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBitwise_not"):
                listener.exitBitwise_not(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitBitwise_not"):
                return visitor.visitBitwise_not(self)
            else:
                return visitor.visitChildren(self)




    def bitwise_not(self):

        localctx = ADQLParser.Bitwise_notContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_bitwise_not)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 279
            self.match(ADQLParser.TILDE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Bitwise_orContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Bitwise_orContext, self).__init__(parent, invokingState)
            self.parser = parser

        def VERTBAR(self):
            return self.getToken(ADQLParser.VERTBAR, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_bitwise_or

        def enterRule(self, listener):
            if hasattr(listener, "enterBitwise_or"):
                listener.enterBitwise_or(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBitwise_or"):
                listener.exitBitwise_or(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitBitwise_or"):
                return visitor.visitBitwise_or(self)
            else:
                return visitor.visitChildren(self)




    def bitwise_or(self):

        localctx = ADQLParser.Bitwise_orContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_bitwise_or)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 281
            self.match(ADQLParser.VERTBAR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Bitwise_xorContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Bitwise_xorContext, self).__init__(parent, invokingState)
            self.parser = parser

        def CIRCUMFLEX(self):
            return self.getToken(ADQLParser.CIRCUMFLEX, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_bitwise_xor

        def enterRule(self, listener):
            if hasattr(listener, "enterBitwise_xor"):
                listener.enterBitwise_xor(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBitwise_xor"):
                listener.exitBitwise_xor(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitBitwise_xor"):
                return visitor.visitBitwise_xor(self)
            else:
                return visitor.visitChildren(self)




    def bitwise_xor(self):

        localctx = ADQLParser.Bitwise_xorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_bitwise_xor)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 283
            self.match(ADQLParser.CIRCUMFLEX)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Boolean_factorContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Boolean_factorContext, self).__init__(parent, invokingState)
            self.parser = parser

        def boolean_primary(self):
            return self.getTypedRuleContext(ADQLParser.Boolean_primaryContext,0)


        def NOT(self):
            return self.getToken(ADQLParser.NOT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_boolean_factor

        def enterRule(self, listener):
            if hasattr(listener, "enterBoolean_factor"):
                listener.enterBoolean_factor(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBoolean_factor"):
                listener.exitBoolean_factor(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitBoolean_factor"):
                return visitor.visitBoolean_factor(self)
            else:
                return visitor.visitChildren(self)




    def boolean_factor(self):

        localctx = ADQLParser.Boolean_factorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_boolean_factor)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 286
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.NOT:
                self.state = 285
                self.match(ADQLParser.NOT)


            self.state = 288
            self.boolean_primary()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Boolean_literalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Boolean_literalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def TRUE(self):
            return self.getToken(ADQLParser.TRUE, 0)

        def FALSE(self):
            return self.getToken(ADQLParser.FALSE, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_boolean_literal

        def enterRule(self, listener):
            if hasattr(listener, "enterBoolean_literal"):
                listener.enterBoolean_literal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBoolean_literal"):
                listener.exitBoolean_literal(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitBoolean_literal"):
                return visitor.visitBoolean_literal(self)
            else:
                return visitor.visitChildren(self)




    def boolean_literal(self):

        localctx = ADQLParser.Boolean_literalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_boolean_literal)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 290
            _la = self._input.LA(1)
            if not(_la==ADQLParser.FALSE or _la==ADQLParser.TRUE):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Boolean_primaryContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Boolean_primaryContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def search_condition(self):
            return self.getTypedRuleContext(ADQLParser.Search_conditionContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def predicate(self):
            return self.getTypedRuleContext(ADQLParser.PredicateContext,0)


        def boolean_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Boolean_value_expressionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_boolean_primary

        def enterRule(self, listener):
            if hasattr(listener, "enterBoolean_primary"):
                listener.enterBoolean_primary(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBoolean_primary"):
                listener.exitBoolean_primary(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitBoolean_primary"):
                return visitor.visitBoolean_primary(self)
            else:
                return visitor.visitChildren(self)




    def boolean_primary(self):

        localctx = ADQLParser.Boolean_primaryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_boolean_primary)
        try:
            self.state = 298
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 292
                self.match(ADQLParser.LPAREN)
                self.state = 293
                self.search_condition(0)
                self.state = 294
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 296
                self.predicate()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 297
                self.boolean_value_expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Boolean_termContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Boolean_termContext, self).__init__(parent, invokingState)
            self.parser = parser

        def boolean_factor(self):
            return self.getTypedRuleContext(ADQLParser.Boolean_factorContext,0)


        def boolean_term(self):
            return self.getTypedRuleContext(ADQLParser.Boolean_termContext,0)


        def AND(self):
            return self.getToken(ADQLParser.AND, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_boolean_term

        def enterRule(self, listener):
            if hasattr(listener, "enterBoolean_term"):
                listener.enterBoolean_term(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBoolean_term"):
                listener.exitBoolean_term(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitBoolean_term"):
                return visitor.visitBoolean_term(self)
            else:
                return visitor.visitChildren(self)



    def boolean_term(self, _p=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ADQLParser.Boolean_termContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 22
        self.enterRecursionRule(localctx, 22, self.RULE_boolean_term, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 301
            self.boolean_factor()
            self._ctx.stop = self._input.LT(-1)
            self.state = 308
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,4,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = ADQLParser.Boolean_termContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_boolean_term)
                    self.state = 303
                    if not self.precpred(self._ctx, 1):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                    self.state = 304
                    self.match(ADQLParser.AND)
                    self.state = 305
                    self.boolean_factor() 
                self.state = 310
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class Boolean_value_expressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Boolean_value_expressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def boolean_literal(self):
            return self.getTypedRuleContext(ADQLParser.Boolean_literalContext,0)


        def user_defined_function(self):
            return self.getTypedRuleContext(ADQLParser.User_defined_functionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_boolean_value_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterBoolean_value_expression"):
                listener.enterBoolean_value_expression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBoolean_value_expression"):
                listener.exitBoolean_value_expression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitBoolean_value_expression"):
                return visitor.visitBoolean_value_expression(self)
            else:
                return visitor.visitChildren(self)




    def boolean_value_expression(self):

        localctx = ADQLParser.Boolean_value_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_boolean_value_expression)
        try:
            self.state = 313
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.FALSE, ADQLParser.TRUE]:
                self.enterOuterAlt(localctx, 1)
                self.state = 311
                self.boolean_literal()
                pass
            elif token in [ADQLParser.ID]:
                self.enterOuterAlt(localctx, 2)
                self.state = 312
                self.user_defined_function()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class BoxContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.BoxContext, self).__init__(parent, invokingState)
            self.parser = parser

        def BOX(self):
            return self.getToken(ADQLParser.BOX, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def coord_sys(self):
            return self.getTypedRuleContext(ADQLParser.Coord_sysContext,0)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.COMMA)
            else:
                return self.getToken(ADQLParser.COMMA, i)

        def coordinates(self):
            return self.getTypedRuleContext(ADQLParser.CoordinatesContext,0)


        def numeric_value_expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Numeric_value_expressionContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Numeric_value_expressionContext,i)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_box

        def enterRule(self, listener):
            if hasattr(listener, "enterBox"):
                listener.enterBox(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBox"):
                listener.exitBox(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitBox"):
                return visitor.visitBox(self)
            else:
                return visitor.visitChildren(self)




    def box(self):

        localctx = ADQLParser.BoxContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_box)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 315
            self.match(ADQLParser.BOX)
            self.state = 316
            self.match(ADQLParser.LPAREN)
            self.state = 317
            self.coord_sys()
            self.state = 318
            self.match(ADQLParser.COMMA)
            self.state = 319
            self.coordinates()
            self.state = 320
            self.match(ADQLParser.COMMA)
            self.state = 321
            self.numeric_value_expression(0)
            self.state = 322
            self.match(ADQLParser.COMMA)
            self.state = 323
            self.numeric_value_expression(0)
            self.state = 324
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Catalog_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Catalog_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(ADQLParser.ID, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_catalog_name

        def enterRule(self, listener):
            if hasattr(listener, "enterCatalog_name"):
                listener.enterCatalog_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCatalog_name"):
                listener.exitCatalog_name(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCatalog_name"):
                return visitor.visitCatalog_name(self)
            else:
                return visitor.visitChildren(self)




    def catalog_name(self):

        localctx = ADQLParser.Catalog_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_catalog_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 326
            self.match(ADQLParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class CentroidContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.CentroidContext, self).__init__(parent, invokingState)
            self.parser = parser

        def CENTROID(self):
            return self.getToken(ADQLParser.CENTROID, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def geometry_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Geometry_value_expressionContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_centroid

        def enterRule(self, listener):
            if hasattr(listener, "enterCentroid"):
                listener.enterCentroid(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCentroid"):
                listener.exitCentroid(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCentroid"):
                return visitor.visitCentroid(self)
            else:
                return visitor.visitChildren(self)




    def centroid(self):

        localctx = ADQLParser.CentroidContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_centroid)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 328
            self.match(ADQLParser.CENTROID)
            self.state = 329
            self.match(ADQLParser.LPAREN)
            self.state = 330
            self.geometry_value_expression()
            self.state = 331
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Character_string_literalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Character_string_literalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def SQ(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.SQ)
            else:
                return self.getToken(ADQLParser.SQ, i)

        def ID(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.ID)
            else:
                return self.getToken(ADQLParser.ID, i)

        def getRuleIndex(self):
            return ADQLParser.RULE_character_string_literal

        def enterRule(self, listener):
            if hasattr(listener, "enterCharacter_string_literal"):
                listener.enterCharacter_string_literal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCharacter_string_literal"):
                listener.exitCharacter_string_literal(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCharacter_string_literal"):
                return visitor.visitCharacter_string_literal(self)
            else:
                return visitor.visitChildren(self)




    def character_string_literal(self):

        localctx = ADQLParser.Character_string_literalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_character_string_literal)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 333
            self.match(ADQLParser.SQ)
            self.state = 337
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==ADQLParser.ID:
                self.state = 334
                self.match(ADQLParser.ID)
                self.state = 339
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 340
            self.match(ADQLParser.SQ)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Character_value_expressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Character_value_expressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def value_expression_primary(self):
            return self.getTypedRuleContext(ADQLParser.Value_expression_primaryContext,0)


        def string_value_function(self):
            return self.getTypedRuleContext(ADQLParser.String_value_functionContext,0)


        def character_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Character_value_expressionContext,0)


        def concatenation_operator(self):
            return self.getTypedRuleContext(ADQLParser.Concatenation_operatorContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_character_value_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterCharacter_value_expression"):
                listener.enterCharacter_value_expression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCharacter_value_expression"):
                listener.exitCharacter_value_expression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCharacter_value_expression"):
                return visitor.visitCharacter_value_expression(self)
            else:
                return visitor.visitChildren(self)



    def character_value_expression(self, _p=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ADQLParser.Character_value_expressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 34
        self.enterRecursionRule(localctx, 34, self.RULE_character_value_expression, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 345
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,7,self._ctx)
            if la_ == 1:
                self.state = 343
                self.value_expression_primary()
                pass

            elif la_ == 2:
                self.state = 344
                self.string_value_function()
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 355
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,9,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = ADQLParser.Character_value_expressionContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_character_value_expression)
                    self.state = 347
                    if not self.precpred(self._ctx, 3):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                    self.state = 348
                    self.concatenation_operator()
                    self.state = 351
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,8,self._ctx)
                    if la_ == 1:
                        self.state = 349
                        self.value_expression_primary()
                        pass

                    elif la_ == 2:
                        self.state = 350
                        self.string_value_function()
                        pass

             
                self.state = 357
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,9,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class CircleContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.CircleContext, self).__init__(parent, invokingState)
            self.parser = parser

        def CIRCLE(self):
            return self.getToken(ADQLParser.CIRCLE, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def coord_sys(self):
            return self.getTypedRuleContext(ADQLParser.Coord_sysContext,0)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.COMMA)
            else:
                return self.getToken(ADQLParser.COMMA, i)

        def coordinates(self):
            return self.getTypedRuleContext(ADQLParser.CoordinatesContext,0)


        def radius(self):
            return self.getTypedRuleContext(ADQLParser.RadiusContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_circle

        def enterRule(self, listener):
            if hasattr(listener, "enterCircle"):
                listener.enterCircle(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCircle"):
                listener.exitCircle(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCircle"):
                return visitor.visitCircle(self)
            else:
                return visitor.visitChildren(self)




    def circle(self):

        localctx = ADQLParser.CircleContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_circle)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 358
            self.match(ADQLParser.CIRCLE)
            self.state = 359
            self.match(ADQLParser.LPAREN)
            self.state = 360
            self.coord_sys()
            self.state = 361
            self.match(ADQLParser.COMMA)
            self.state = 362
            self.coordinates()
            self.state = 363
            self.match(ADQLParser.COMMA)
            self.state = 364
            self.radius()
            self.state = 365
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Column_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Column_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(ADQLParser.IdentifierContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_column_name

        def enterRule(self, listener):
            if hasattr(listener, "enterColumn_name"):
                listener.enterColumn_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitColumn_name"):
                listener.exitColumn_name(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitColumn_name"):
                return visitor.visitColumn_name(self)
            else:
                return visitor.visitChildren(self)




    def column_name(self):

        localctx = ADQLParser.Column_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_column_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 367
            self.identifier()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Column_name_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Column_name_listContext, self).__init__(parent, invokingState)
            self.parser = parser

        def column_name(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Column_nameContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Column_nameContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.COMMA)
            else:
                return self.getToken(ADQLParser.COMMA, i)

        def getRuleIndex(self):
            return ADQLParser.RULE_column_name_list

        def enterRule(self, listener):
            if hasattr(listener, "enterColumn_name_list"):
                listener.enterColumn_name_list(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitColumn_name_list"):
                listener.exitColumn_name_list(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitColumn_name_list"):
                return visitor.visitColumn_name_list(self)
            else:
                return visitor.visitChildren(self)




    def column_name_list(self):

        localctx = ADQLParser.Column_name_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_column_name_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 369
            self.column_name()
            self.state = 374
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==ADQLParser.COMMA:
                self.state = 370
                self.match(ADQLParser.COMMA)
                self.state = 371
                self.column_name()
                self.state = 376
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Column_referenceContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Column_referenceContext, self).__init__(parent, invokingState)
            self.parser = parser

        def column_name(self):
            return self.getTypedRuleContext(ADQLParser.Column_nameContext,0)


        def qualifier(self):
            return self.getTypedRuleContext(ADQLParser.QualifierContext,0)


        def DOT(self):
            return self.getToken(ADQLParser.DOT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_column_reference

        def enterRule(self, listener):
            if hasattr(listener, "enterColumn_reference"):
                listener.enterColumn_reference(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitColumn_reference"):
                listener.exitColumn_reference(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitColumn_reference"):
                return visitor.visitColumn_reference(self)
            else:
                return visitor.visitChildren(self)




    def column_reference(self):

        localctx = ADQLParser.Column_referenceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_column_reference)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 380
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,11,self._ctx)
            if la_ == 1:
                self.state = 377
                self.qualifier()
                self.state = 378
                self.match(ADQLParser.DOT)


            self.state = 382
            self.column_name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Comp_opContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Comp_opContext, self).__init__(parent, invokingState)
            self.parser = parser

        def EQ(self):
            return self.getToken(ADQLParser.EQ, 0)

        def NOT_EQ(self):
            return self.getToken(ADQLParser.NOT_EQ, 0)

        def LTH(self):
            return self.getToken(ADQLParser.LTH, 0)

        def GTH(self):
            return self.getToken(ADQLParser.GTH, 0)

        def GRET(self):
            return self.getToken(ADQLParser.GRET, 0)

        def LEET(self):
            return self.getToken(ADQLParser.LEET, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_comp_op

        def enterRule(self, listener):
            if hasattr(listener, "enterComp_op"):
                listener.enterComp_op(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitComp_op"):
                listener.exitComp_op(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitComp_op"):
                return visitor.visitComp_op(self)
            else:
                return visitor.visitChildren(self)




    def comp_op(self):

        localctx = ADQLParser.Comp_opContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_comp_op)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 384
            _la = self._input.LA(1)
            if not(((((_la - 289)) & ~0x3f) == 0 and ((1 << (_la - 289)) & ((1 << (ADQLParser.LTH - 289)) | (1 << (ADQLParser.EQ - 289)) | (1 << (ADQLParser.GTH - 289)) | (1 << (ADQLParser.LEET - 289)) | (1 << (ADQLParser.GRET - 289)) | (1 << (ADQLParser.NOT_EQ - 289)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Comparison_predicateContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Comparison_predicateContext, self).__init__(parent, invokingState)
            self.parser = parser

        def value_expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Value_expressionContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Value_expressionContext,i)


        def comp_op(self):
            return self.getTypedRuleContext(ADQLParser.Comp_opContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_comparison_predicate

        def enterRule(self, listener):
            if hasattr(listener, "enterComparison_predicate"):
                listener.enterComparison_predicate(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitComparison_predicate"):
                listener.exitComparison_predicate(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitComparison_predicate"):
                return visitor.visitComparison_predicate(self)
            else:
                return visitor.visitChildren(self)




    def comparison_predicate(self):

        localctx = ADQLParser.Comparison_predicateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_comparison_predicate)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 386
            self.value_expression()
            self.state = 387
            self.comp_op()
            self.state = 388
            self.value_expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Concatenation_operatorContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Concatenation_operatorContext, self).__init__(parent, invokingState)
            self.parser = parser

        def CONCAT(self):
            return self.getToken(ADQLParser.CONCAT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_concatenation_operator

        def enterRule(self, listener):
            if hasattr(listener, "enterConcatenation_operator"):
                listener.enterConcatenation_operator(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitConcatenation_operator"):
                listener.exitConcatenation_operator(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitConcatenation_operator"):
                return visitor.visitConcatenation_operator(self)
            else:
                return visitor.visitChildren(self)




    def concatenation_operator(self):

        localctx = ADQLParser.Concatenation_operatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_concatenation_operator)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 390
            self.match(ADQLParser.CONCAT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ContainsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.ContainsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def CONTAINS(self):
            return self.getToken(ADQLParser.CONTAINS, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def geometry_value_expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Geometry_value_expressionContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Geometry_value_expressionContext,i)


        def COMMA(self):
            return self.getToken(ADQLParser.COMMA, 0)

        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_contains

        def enterRule(self, listener):
            if hasattr(listener, "enterContains"):
                listener.enterContains(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitContains"):
                listener.exitContains(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitContains"):
                return visitor.visitContains(self)
            else:
                return visitor.visitChildren(self)




    def contains(self):

        localctx = ADQLParser.ContainsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_contains)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 392
            self.match(ADQLParser.CONTAINS)
            self.state = 393
            self.match(ADQLParser.LPAREN)
            self.state = 394
            self.geometry_value_expression()
            self.state = 395
            self.match(ADQLParser.COMMA)
            self.state = 396
            self.geometry_value_expression()
            self.state = 397
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Coord_sysContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Coord_sysContext, self).__init__(parent, invokingState)
            self.parser = parser

        def string_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.String_value_expressionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_coord_sys

        def enterRule(self, listener):
            if hasattr(listener, "enterCoord_sys"):
                listener.enterCoord_sys(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCoord_sys"):
                listener.exitCoord_sys(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCoord_sys"):
                return visitor.visitCoord_sys(self)
            else:
                return visitor.visitChildren(self)




    def coord_sys(self):

        localctx = ADQLParser.Coord_sysContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_coord_sys)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 399
            self.string_value_expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Coord_valueContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Coord_valueContext, self).__init__(parent, invokingState)
            self.parser = parser

        def point(self):
            return self.getTypedRuleContext(ADQLParser.PointContext,0)


        def column_reference(self):
            return self.getTypedRuleContext(ADQLParser.Column_referenceContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_coord_value

        def enterRule(self, listener):
            if hasattr(listener, "enterCoord_value"):
                listener.enterCoord_value(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCoord_value"):
                listener.exitCoord_value(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCoord_value"):
                return visitor.visitCoord_value(self)
            else:
                return visitor.visitChildren(self)




    def coord_value(self):

        localctx = ADQLParser.Coord_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_coord_value)
        try:
            self.state = 403
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.POINT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 401
                self.point()
                pass
            elif token in [ADQLParser.ID, ADQLParser.DQ]:
                self.enterOuterAlt(localctx, 2)
                self.state = 402
                self.column_reference()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Coord1Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Coord1Context, self).__init__(parent, invokingState)
            self.parser = parser

        def COORD1(self):
            return self.getToken(ADQLParser.COORD1, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def coord_value(self):
            return self.getTypedRuleContext(ADQLParser.Coord_valueContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_coord1

        def enterRule(self, listener):
            if hasattr(listener, "enterCoord1"):
                listener.enterCoord1(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCoord1"):
                listener.exitCoord1(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCoord1"):
                return visitor.visitCoord1(self)
            else:
                return visitor.visitChildren(self)




    def coord1(self):

        localctx = ADQLParser.Coord1Context(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_coord1)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 405
            self.match(ADQLParser.COORD1)
            self.state = 406
            self.match(ADQLParser.LPAREN)
            self.state = 407
            self.coord_value()
            self.state = 408
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Coord2Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Coord2Context, self).__init__(parent, invokingState)
            self.parser = parser

        def COORD2(self):
            return self.getToken(ADQLParser.COORD2, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def coord_value(self):
            return self.getTypedRuleContext(ADQLParser.Coord_valueContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_coord2

        def enterRule(self, listener):
            if hasattr(listener, "enterCoord2"):
                listener.enterCoord2(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCoord2"):
                listener.exitCoord2(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCoord2"):
                return visitor.visitCoord2(self)
            else:
                return visitor.visitChildren(self)




    def coord2(self):

        localctx = ADQLParser.Coord2Context(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_coord2)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 410
            self.match(ADQLParser.COORD2)
            self.state = 411
            self.match(ADQLParser.LPAREN)
            self.state = 412
            self.coord_value()
            self.state = 413
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Coordinate1Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Coordinate1Context, self).__init__(parent, invokingState)
            self.parser = parser

        def numeric_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Numeric_value_expressionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_coordinate1

        def enterRule(self, listener):
            if hasattr(listener, "enterCoordinate1"):
                listener.enterCoordinate1(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCoordinate1"):
                listener.exitCoordinate1(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCoordinate1"):
                return visitor.visitCoordinate1(self)
            else:
                return visitor.visitChildren(self)




    def coordinate1(self):

        localctx = ADQLParser.Coordinate1Context(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_coordinate1)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 415
            self.numeric_value_expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Coordinate2Context(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Coordinate2Context, self).__init__(parent, invokingState)
            self.parser = parser

        def numeric_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Numeric_value_expressionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_coordinate2

        def enterRule(self, listener):
            if hasattr(listener, "enterCoordinate2"):
                listener.enterCoordinate2(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCoordinate2"):
                listener.exitCoordinate2(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCoordinate2"):
                return visitor.visitCoordinate2(self)
            else:
                return visitor.visitChildren(self)




    def coordinate2(self):

        localctx = ADQLParser.Coordinate2Context(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_coordinate2)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 417
            self.numeric_value_expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class CoordinatesContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.CoordinatesContext, self).__init__(parent, invokingState)
            self.parser = parser

        def coordinate1(self):
            return self.getTypedRuleContext(ADQLParser.Coordinate1Context,0)


        def COMMA(self):
            return self.getToken(ADQLParser.COMMA, 0)

        def coordinate2(self):
            return self.getTypedRuleContext(ADQLParser.Coordinate2Context,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_coordinates

        def enterRule(self, listener):
            if hasattr(listener, "enterCoordinates"):
                listener.enterCoordinates(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCoordinates"):
                listener.exitCoordinates(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCoordinates"):
                return visitor.visitCoordinates(self)
            else:
                return visitor.visitChildren(self)




    def coordinates(self):

        localctx = ADQLParser.CoordinatesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_coordinates)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 419
            self.coordinate1()
            self.state = 420
            self.match(ADQLParser.COMMA)
            self.state = 421
            self.coordinate2()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Correlation_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Correlation_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(ADQLParser.IdentifierContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_correlation_name

        def enterRule(self, listener):
            if hasattr(listener, "enterCorrelation_name"):
                listener.enterCorrelation_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCorrelation_name"):
                listener.exitCorrelation_name(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCorrelation_name"):
                return visitor.visitCorrelation_name(self)
            else:
                return visitor.visitChildren(self)




    def correlation_name(self):

        localctx = ADQLParser.Correlation_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_correlation_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 423
            self.identifier()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Correlation_specificationContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Correlation_specificationContext, self).__init__(parent, invokingState)
            self.parser = parser

        def correlation_name(self):
            return self.getTypedRuleContext(ADQLParser.Correlation_nameContext,0)


        def AS(self):
            return self.getToken(ADQLParser.AS, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_correlation_specification

        def enterRule(self, listener):
            if hasattr(listener, "enterCorrelation_specification"):
                listener.enterCorrelation_specification(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitCorrelation_specification"):
                listener.exitCorrelation_specification(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitCorrelation_specification"):
                return visitor.visitCorrelation_specification(self)
            else:
                return visitor.visitChildren(self)




    def correlation_specification(self):

        localctx = ADQLParser.Correlation_specificationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_correlation_specification)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 426
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.AS:
                self.state = 425
                self.match(ADQLParser.AS)


            self.state = 428
            self.correlation_name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Delimited_identifierContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Delimited_identifierContext, self).__init__(parent, invokingState)
            self.parser = parser

        def DQ(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.DQ)
            else:
                return self.getToken(ADQLParser.DQ, i)

        def ID(self):
            return self.getToken(ADQLParser.ID, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_delimited_identifier

        def enterRule(self, listener):
            if hasattr(listener, "enterDelimited_identifier"):
                listener.enterDelimited_identifier(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDelimited_identifier"):
                listener.exitDelimited_identifier(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitDelimited_identifier"):
                return visitor.visitDelimited_identifier(self)
            else:
                return visitor.visitChildren(self)




    def delimited_identifier(self):

        localctx = ADQLParser.Delimited_identifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_delimited_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 430
            self.match(ADQLParser.DQ)
            self.state = 431
            self.match(ADQLParser.ID)
            self.state = 432
            self.match(ADQLParser.DQ)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Derived_columnContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Derived_columnContext, self).__init__(parent, invokingState)
            self.parser = parser

        def value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Value_expressionContext,0)


        def as_clause(self):
            return self.getTypedRuleContext(ADQLParser.As_clauseContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_derived_column

        def enterRule(self, listener):
            if hasattr(listener, "enterDerived_column"):
                listener.enterDerived_column(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDerived_column"):
                listener.exitDerived_column(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitDerived_column"):
                return visitor.visitDerived_column(self)
            else:
                return visitor.visitChildren(self)




    def derived_column(self):

        localctx = ADQLParser.Derived_columnContext(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_derived_column)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 434
            self.value_expression()
            self.state = 436
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.AS or _la==ADQLParser.ID or _la==ADQLParser.DQ:
                self.state = 435
                self.as_clause()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Derived_tableContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Derived_tableContext, self).__init__(parent, invokingState)
            self.parser = parser

        def table_subquery(self):
            return self.getTypedRuleContext(ADQLParser.Table_subqueryContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_derived_table

        def enterRule(self, listener):
            if hasattr(listener, "enterDerived_table"):
                listener.enterDerived_table(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDerived_table"):
                listener.exitDerived_table(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitDerived_table"):
                return visitor.visitDerived_table(self)
            else:
                return visitor.visitChildren(self)




    def derived_table(self):

        localctx = ADQLParser.Derived_tableContext(self, self._ctx, self.state)
        self.enterRule(localctx, 74, self.RULE_derived_table)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 438
            self.table_subquery()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DistanceContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.DistanceContext, self).__init__(parent, invokingState)
            self.parser = parser

        def DISTANCE(self):
            return self.getToken(ADQLParser.DISTANCE, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def coord_value(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Coord_valueContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Coord_valueContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.COMMA)
            else:
                return self.getToken(ADQLParser.COMMA, i)

        def numeric_value_expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Numeric_value_expressionContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Numeric_value_expressionContext,i)


        def getRuleIndex(self):
            return ADQLParser.RULE_distance

        def enterRule(self, listener):
            if hasattr(listener, "enterDistance"):
                listener.enterDistance(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitDistance"):
                listener.exitDistance(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitDistance"):
                return visitor.visitDistance(self)
            else:
                return visitor.visitChildren(self)




    def distance(self):

        localctx = ADQLParser.DistanceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_distance)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 440
            self.match(ADQLParser.DISTANCE)
            self.state = 441
            self.match(ADQLParser.LPAREN)
            self.state = 454
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,15,self._ctx)
            if la_ == 1:
                self.state = 442
                self.coord_value()
                self.state = 443
                self.match(ADQLParser.COMMA)
                self.state = 444
                self.coord_value()
                pass

            elif la_ == 2:
                self.state = 446
                self.numeric_value_expression(0)
                self.state = 447
                self.match(ADQLParser.COMMA)
                self.state = 448
                self.numeric_value_expression(0)
                self.state = 449
                self.match(ADQLParser.COMMA)
                self.state = 450
                self.numeric_value_expression(0)
                self.state = 451
                self.match(ADQLParser.COMMA)
                self.state = 452
                self.numeric_value_expression(0)
                pass


            self.state = 456
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Exact_numeric_literalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Exact_numeric_literalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def unsigned_decimal(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Unsigned_decimalContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Unsigned_decimalContext,i)


        def DOT(self):
            return self.getToken(ADQLParser.DOT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_exact_numeric_literal

        def enterRule(self, listener):
            if hasattr(listener, "enterExact_numeric_literal"):
                listener.enterExact_numeric_literal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitExact_numeric_literal"):
                listener.exitExact_numeric_literal(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitExact_numeric_literal"):
                return visitor.visitExact_numeric_literal(self)
            else:
                return visitor.visitChildren(self)




    def exact_numeric_literal(self):

        localctx = ADQLParser.Exact_numeric_literalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_exact_numeric_literal)
        try:
            self.state = 467
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.INT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 458
                self.unsigned_decimal()
                self.state = 463
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,17,self._ctx)
                if la_ == 1:
                    self.state = 459
                    self.match(ADQLParser.DOT)
                    self.state = 461
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,16,self._ctx)
                    if la_ == 1:
                        self.state = 460
                        self.unsigned_decimal()




                pass
            elif token in [ADQLParser.DOT]:
                self.enterOuterAlt(localctx, 2)
                self.state = 465
                self.match(ADQLParser.DOT)
                self.state = 466
                self.unsigned_decimal()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Exists_predicateContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Exists_predicateContext, self).__init__(parent, invokingState)
            self.parser = parser

        def EXISTS(self):
            return self.getToken(ADQLParser.EXISTS, 0)

        def table_subquery(self):
            return self.getTypedRuleContext(ADQLParser.Table_subqueryContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_exists_predicate

        def enterRule(self, listener):
            if hasattr(listener, "enterExists_predicate"):
                listener.enterExists_predicate(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitExists_predicate"):
                listener.exitExists_predicate(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitExists_predicate"):
                return visitor.visitExists_predicate(self)
            else:
                return visitor.visitChildren(self)




    def exists_predicate(self):

        localctx = ADQLParser.Exists_predicateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 80, self.RULE_exists_predicate)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 469
            self.match(ADQLParser.EXISTS)
            self.state = 470
            self.table_subquery()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Extract_coordsysContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Extract_coordsysContext, self).__init__(parent, invokingState)
            self.parser = parser

        def COORDSYS(self):
            return self.getToken(ADQLParser.COORDSYS, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def geometry_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Geometry_value_expressionContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_extract_coordsys

        def enterRule(self, listener):
            if hasattr(listener, "enterExtract_coordsys"):
                listener.enterExtract_coordsys(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitExtract_coordsys"):
                listener.exitExtract_coordsys(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitExtract_coordsys"):
                return visitor.visitExtract_coordsys(self)
            else:
                return visitor.visitChildren(self)




    def extract_coordsys(self):

        localctx = ADQLParser.Extract_coordsysContext(self, self._ctx, self.state)
        self.enterRule(localctx, 82, self.RULE_extract_coordsys)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 472
            self.match(ADQLParser.COORDSYS)
            self.state = 473
            self.match(ADQLParser.LPAREN)
            self.state = 474
            self.geometry_value_expression()
            self.state = 475
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FactorContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.FactorContext, self).__init__(parent, invokingState)
            self.parser = parser

        def numeric_primary(self):
            return self.getTypedRuleContext(ADQLParser.Numeric_primaryContext,0)


        def sign(self):
            return self.getTypedRuleContext(ADQLParser.SignContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_factor

        def enterRule(self, listener):
            if hasattr(listener, "enterFactor"):
                listener.enterFactor(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFactor"):
                listener.exitFactor(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitFactor"):
                return visitor.visitFactor(self)
            else:
                return visitor.visitChildren(self)




    def factor(self):

        localctx = ADQLParser.FactorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 84, self.RULE_factor)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 478
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,19,self._ctx)
            if la_ == 1:
                self.state = 477
                self.sign()


            self.state = 480
            self.numeric_primary()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class From_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.From_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def FROM(self):
            return self.getToken(ADQLParser.FROM, 0)

        def table_reference(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Table_referenceContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Table_referenceContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.COMMA)
            else:
                return self.getToken(ADQLParser.COMMA, i)

        def getRuleIndex(self):
            return ADQLParser.RULE_from_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterFrom_clause"):
                listener.enterFrom_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitFrom_clause"):
                listener.exitFrom_clause(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitFrom_clause"):
                return visitor.visitFrom_clause(self)
            else:
                return visitor.visitChildren(self)




    def from_clause(self):

        localctx = ADQLParser.From_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 86, self.RULE_from_clause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 482
            self.match(ADQLParser.FROM)
            self.state = 483
            self.table_reference(0)
            self.state = 488
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==ADQLParser.COMMA:
                self.state = 484
                self.match(ADQLParser.COMMA)
                self.state = 485
                self.table_reference(0)
                self.state = 490
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class General_literalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.General_literalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def character_string_literal(self):
            return self.getTypedRuleContext(ADQLParser.Character_string_literalContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_general_literal

        def enterRule(self, listener):
            if hasattr(listener, "enterGeneral_literal"):
                listener.enterGeneral_literal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitGeneral_literal"):
                listener.exitGeneral_literal(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitGeneral_literal"):
                return visitor.visitGeneral_literal(self)
            else:
                return visitor.visitChildren(self)




    def general_literal(self):

        localctx = ADQLParser.General_literalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 88, self.RULE_general_literal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 491
            self.character_string_literal()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class General_set_functionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.General_set_functionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def set_function_type(self):
            return self.getTypedRuleContext(ADQLParser.Set_function_typeContext,0)


        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Value_expressionContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def set_quantifier(self):
            return self.getTypedRuleContext(ADQLParser.Set_quantifierContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_general_set_function

        def enterRule(self, listener):
            if hasattr(listener, "enterGeneral_set_function"):
                listener.enterGeneral_set_function(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitGeneral_set_function"):
                listener.exitGeneral_set_function(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitGeneral_set_function"):
                return visitor.visitGeneral_set_function(self)
            else:
                return visitor.visitChildren(self)




    def general_set_function(self):

        localctx = ADQLParser.General_set_functionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 90, self.RULE_general_set_function)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 493
            self.set_function_type()
            self.state = 494
            self.match(ADQLParser.LPAREN)
            self.state = 496
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.ALL or _la==ADQLParser.DISTINCT:
                self.state = 495
                self.set_quantifier()


            self.state = 498
            self.value_expression()
            self.state = 499
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Geometry_value_expressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Geometry_value_expressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def box(self):
            return self.getTypedRuleContext(ADQLParser.BoxContext,0)


        def centroid(self):
            return self.getTypedRuleContext(ADQLParser.CentroidContext,0)


        def circle(self):
            return self.getTypedRuleContext(ADQLParser.CircleContext,0)


        def point(self):
            return self.getTypedRuleContext(ADQLParser.PointContext,0)


        def polygon(self):
            return self.getTypedRuleContext(ADQLParser.PolygonContext,0)


        def region(self):
            return self.getTypedRuleContext(ADQLParser.RegionContext,0)


        def user_defined_function(self):
            return self.getTypedRuleContext(ADQLParser.User_defined_functionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_geometry_value_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterGeometry_value_expression"):
                listener.enterGeometry_value_expression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitGeometry_value_expression"):
                listener.exitGeometry_value_expression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitGeometry_value_expression"):
                return visitor.visitGeometry_value_expression(self)
            else:
                return visitor.visitChildren(self)




    def geometry_value_expression(self):

        localctx = ADQLParser.Geometry_value_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 92, self.RULE_geometry_value_expression)
        try:
            self.state = 508
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.BOX]:
                self.enterOuterAlt(localctx, 1)
                self.state = 501
                self.box()
                pass
            elif token in [ADQLParser.CENTROID]:
                self.enterOuterAlt(localctx, 2)
                self.state = 502
                self.centroid()
                pass
            elif token in [ADQLParser.CIRCLE]:
                self.enterOuterAlt(localctx, 3)
                self.state = 503
                self.circle()
                pass
            elif token in [ADQLParser.POINT]:
                self.enterOuterAlt(localctx, 4)
                self.state = 504
                self.point()
                pass
            elif token in [ADQLParser.POLYGON]:
                self.enterOuterAlt(localctx, 5)
                self.state = 505
                self.polygon()
                pass
            elif token in [ADQLParser.REGION]:
                self.enterOuterAlt(localctx, 6)
                self.state = 506
                self.region()
                pass
            elif token in [ADQLParser.ID]:
                self.enterOuterAlt(localctx, 7)
                self.state = 507
                self.user_defined_function()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Group_by_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Group_by_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def GROUP(self):
            return self.getToken(ADQLParser.GROUP, 0)

        def BY(self):
            return self.getToken(ADQLParser.BY, 0)

        def grouping_column_reference_list(self):
            return self.getTypedRuleContext(ADQLParser.Grouping_column_reference_listContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_group_by_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterGroup_by_clause"):
                listener.enterGroup_by_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitGroup_by_clause"):
                listener.exitGroup_by_clause(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitGroup_by_clause"):
                return visitor.visitGroup_by_clause(self)
            else:
                return visitor.visitChildren(self)




    def group_by_clause(self):

        localctx = ADQLParser.Group_by_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 94, self.RULE_group_by_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 510
            self.match(ADQLParser.GROUP)
            self.state = 511
            self.match(ADQLParser.BY)
            self.state = 512
            self.grouping_column_reference_list()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Grouping_column_referenceContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Grouping_column_referenceContext, self).__init__(parent, invokingState)
            self.parser = parser

        def column_reference(self):
            return self.getTypedRuleContext(ADQLParser.Column_referenceContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_grouping_column_reference

        def enterRule(self, listener):
            if hasattr(listener, "enterGrouping_column_reference"):
                listener.enterGrouping_column_reference(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitGrouping_column_reference"):
                listener.exitGrouping_column_reference(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitGrouping_column_reference"):
                return visitor.visitGrouping_column_reference(self)
            else:
                return visitor.visitChildren(self)




    def grouping_column_reference(self):

        localctx = ADQLParser.Grouping_column_referenceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 96, self.RULE_grouping_column_reference)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 514
            self.column_reference()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Grouping_column_reference_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Grouping_column_reference_listContext, self).__init__(parent, invokingState)
            self.parser = parser

        def grouping_column_reference(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Grouping_column_referenceContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Grouping_column_referenceContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.COMMA)
            else:
                return self.getToken(ADQLParser.COMMA, i)

        def getRuleIndex(self):
            return ADQLParser.RULE_grouping_column_reference_list

        def enterRule(self, listener):
            if hasattr(listener, "enterGrouping_column_reference_list"):
                listener.enterGrouping_column_reference_list(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitGrouping_column_reference_list"):
                listener.exitGrouping_column_reference_list(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitGrouping_column_reference_list"):
                return visitor.visitGrouping_column_reference_list(self)
            else:
                return visitor.visitChildren(self)




    def grouping_column_reference_list(self):

        localctx = ADQLParser.Grouping_column_reference_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 98, self.RULE_grouping_column_reference_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 516
            self.grouping_column_reference()
            self.state = 521
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==ADQLParser.COMMA:
                self.state = 517
                self.match(ADQLParser.COMMA)
                self.state = 518
                self.grouping_column_reference()
                self.state = 523
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Having_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Having_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def HAVING(self):
            return self.getToken(ADQLParser.HAVING, 0)

        def search_condition(self):
            return self.getTypedRuleContext(ADQLParser.Search_conditionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_having_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterHaving_clause"):
                listener.enterHaving_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitHaving_clause"):
                listener.exitHaving_clause(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitHaving_clause"):
                return visitor.visitHaving_clause(self)
            else:
                return visitor.visitChildren(self)




    def having_clause(self):

        localctx = ADQLParser.Having_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 100, self.RULE_having_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 524
            self.match(ADQLParser.HAVING)
            self.state = 525
            self.search_condition(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class IdentifierContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.IdentifierContext, self).__init__(parent, invokingState)
            self.parser = parser

        def regular_identifier(self):
            return self.getTypedRuleContext(ADQLParser.Regular_identifierContext,0)


        def delimited_identifier(self):
            return self.getTypedRuleContext(ADQLParser.Delimited_identifierContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_identifier

        def enterRule(self, listener):
            if hasattr(listener, "enterIdentifier"):
                listener.enterIdentifier(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitIdentifier"):
                listener.exitIdentifier(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitIdentifier"):
                return visitor.visitIdentifier(self)
            else:
                return visitor.visitChildren(self)




    def identifier(self):

        localctx = ADQLParser.IdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 102, self.RULE_identifier)
        try:
            self.state = 529
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.ID]:
                self.enterOuterAlt(localctx, 1)
                self.state = 527
                self.regular_identifier()
                pass
            elif token in [ADQLParser.DQ]:
                self.enterOuterAlt(localctx, 2)
                self.state = 528
                self.delimited_identifier()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class In_predicateContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.In_predicateContext, self).__init__(parent, invokingState)
            self.parser = parser

        def value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Value_expressionContext,0)


        def IN(self):
            return self.getToken(ADQLParser.IN, 0)

        def in_predicate_value(self):
            return self.getTypedRuleContext(ADQLParser.In_predicate_valueContext,0)


        def NOT(self):
            return self.getToken(ADQLParser.NOT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_in_predicate

        def enterRule(self, listener):
            if hasattr(listener, "enterIn_predicate"):
                listener.enterIn_predicate(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitIn_predicate"):
                listener.exitIn_predicate(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitIn_predicate"):
                return visitor.visitIn_predicate(self)
            else:
                return visitor.visitChildren(self)




    def in_predicate(self):

        localctx = ADQLParser.In_predicateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 104, self.RULE_in_predicate)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 531
            self.value_expression()
            self.state = 533
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.NOT:
                self.state = 532
                self.match(ADQLParser.NOT)


            self.state = 535
            self.match(ADQLParser.IN)
            self.state = 536
            self.in_predicate_value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class In_predicate_valueContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.In_predicate_valueContext, self).__init__(parent, invokingState)
            self.parser = parser

        def table_subquery(self):
            return self.getTypedRuleContext(ADQLParser.Table_subqueryContext,0)


        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def in_value_list(self):
            return self.getTypedRuleContext(ADQLParser.In_value_listContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_in_predicate_value

        def enterRule(self, listener):
            if hasattr(listener, "enterIn_predicate_value"):
                listener.enterIn_predicate_value(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitIn_predicate_value"):
                listener.exitIn_predicate_value(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitIn_predicate_value"):
                return visitor.visitIn_predicate_value(self)
            else:
                return visitor.visitChildren(self)




    def in_predicate_value(self):

        localctx = ADQLParser.In_predicate_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 106, self.RULE_in_predicate_value)
        try:
            self.state = 543
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,26,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 538
                self.table_subquery()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 539
                self.match(ADQLParser.LPAREN)
                self.state = 540
                self.in_value_list()
                self.state = 541
                self.match(ADQLParser.RPAREN)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class In_value_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.In_value_listContext, self).__init__(parent, invokingState)
            self.parser = parser

        def value_expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Value_expressionContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Value_expressionContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.COMMA)
            else:
                return self.getToken(ADQLParser.COMMA, i)

        def getRuleIndex(self):
            return ADQLParser.RULE_in_value_list

        def enterRule(self, listener):
            if hasattr(listener, "enterIn_value_list"):
                listener.enterIn_value_list(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitIn_value_list"):
                listener.exitIn_value_list(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitIn_value_list"):
                return visitor.visitIn_value_list(self)
            else:
                return visitor.visitChildren(self)




    def in_value_list(self):

        localctx = ADQLParser.In_value_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 108, self.RULE_in_value_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 545
            self.value_expression()
            self.state = 548 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 546
                self.match(ADQLParser.COMMA)
                self.state = 547
                self.value_expression()
                self.state = 550 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==ADQLParser.COMMA):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class IntersectsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.IntersectsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def INTERSECTS(self):
            return self.getToken(ADQLParser.INTERSECTS, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def geometry_value_expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Geometry_value_expressionContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Geometry_value_expressionContext,i)


        def COMMA(self):
            return self.getToken(ADQLParser.COMMA, 0)

        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_intersects

        def enterRule(self, listener):
            if hasattr(listener, "enterIntersects"):
                listener.enterIntersects(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitIntersects"):
                listener.exitIntersects(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitIntersects"):
                return visitor.visitIntersects(self)
            else:
                return visitor.visitChildren(self)




    def intersects(self):

        localctx = ADQLParser.IntersectsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 110, self.RULE_intersects)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 552
            self.match(ADQLParser.INTERSECTS)
            self.state = 553
            self.match(ADQLParser.LPAREN)
            self.state = 554
            self.geometry_value_expression()
            self.state = 555
            self.match(ADQLParser.COMMA)
            self.state = 556
            self.geometry_value_expression()
            self.state = 557
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Join_column_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Join_column_listContext, self).__init__(parent, invokingState)
            self.parser = parser

        def column_name_list(self):
            return self.getTypedRuleContext(ADQLParser.Column_name_listContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_join_column_list

        def enterRule(self, listener):
            if hasattr(listener, "enterJoin_column_list"):
                listener.enterJoin_column_list(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitJoin_column_list"):
                listener.exitJoin_column_list(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitJoin_column_list"):
                return visitor.visitJoin_column_list(self)
            else:
                return visitor.visitChildren(self)




    def join_column_list(self):

        localctx = ADQLParser.Join_column_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 112, self.RULE_join_column_list)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 559
            self.column_name_list()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Join_conditionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Join_conditionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ON(self):
            return self.getToken(ADQLParser.ON, 0)

        def search_condition(self):
            return self.getTypedRuleContext(ADQLParser.Search_conditionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_join_condition

        def enterRule(self, listener):
            if hasattr(listener, "enterJoin_condition"):
                listener.enterJoin_condition(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitJoin_condition"):
                listener.exitJoin_condition(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitJoin_condition"):
                return visitor.visitJoin_condition(self)
            else:
                return visitor.visitChildren(self)




    def join_condition(self):

        localctx = ADQLParser.Join_conditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 114, self.RULE_join_condition)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 561
            self.match(ADQLParser.ON)
            self.state = 562
            self.search_condition(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Join_specificationContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Join_specificationContext, self).__init__(parent, invokingState)
            self.parser = parser

        def join_condition(self):
            return self.getTypedRuleContext(ADQLParser.Join_conditionContext,0)


        def named_columns_join(self):
            return self.getTypedRuleContext(ADQLParser.Named_columns_joinContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_join_specification

        def enterRule(self, listener):
            if hasattr(listener, "enterJoin_specification"):
                listener.enterJoin_specification(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitJoin_specification"):
                listener.exitJoin_specification(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitJoin_specification"):
                return visitor.visitJoin_specification(self)
            else:
                return visitor.visitChildren(self)




    def join_specification(self):

        localctx = ADQLParser.Join_specificationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 116, self.RULE_join_specification)
        try:
            self.state = 566
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.ON]:
                self.enterOuterAlt(localctx, 1)
                self.state = 564
                self.join_condition()
                pass
            elif token in [ADQLParser.USING]:
                self.enterOuterAlt(localctx, 2)
                self.state = 565
                self.named_columns_join()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Join_typeContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Join_typeContext, self).__init__(parent, invokingState)
            self.parser = parser

        def INNER(self):
            return self.getToken(ADQLParser.INNER, 0)

        def outer_join_type(self):
            return self.getTypedRuleContext(ADQLParser.Outer_join_typeContext,0)


        def OUTER(self):
            return self.getToken(ADQLParser.OUTER, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_join_type

        def enterRule(self, listener):
            if hasattr(listener, "enterJoin_type"):
                listener.enterJoin_type(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitJoin_type"):
                listener.exitJoin_type(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitJoin_type"):
                return visitor.visitJoin_type(self)
            else:
                return visitor.visitChildren(self)




    def join_type(self):

        localctx = ADQLParser.Join_typeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 118, self.RULE_join_type)
        self._la = 0 # Token type
        try:
            self.state = 573
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.INNER]:
                self.enterOuterAlt(localctx, 1)
                self.state = 568
                self.match(ADQLParser.INNER)
                pass
            elif token in [ADQLParser.FULL, ADQLParser.LEFT, ADQLParser.RIGHT]:
                self.enterOuterAlt(localctx, 2)
                self.state = 569
                self.outer_join_type()
                self.state = 571
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==ADQLParser.OUTER:
                    self.state = 570
                    self.match(ADQLParser.OUTER)


                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Joined_tableContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Joined_tableContext, self).__init__(parent, invokingState)
            self.parser = parser

        def table_reference(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Table_referenceContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Table_referenceContext,i)


        def JOIN(self):
            return self.getToken(ADQLParser.JOIN, 0)

        def NATURAL(self):
            return self.getToken(ADQLParser.NATURAL, 0)

        def join_type(self):
            return self.getTypedRuleContext(ADQLParser.Join_typeContext,0)


        def join_specification(self):
            return self.getTypedRuleContext(ADQLParser.Join_specificationContext,0)


        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def joined_table(self):
            return self.getTypedRuleContext(ADQLParser.Joined_tableContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_joined_table

        def enterRule(self, listener):
            if hasattr(listener, "enterJoined_table"):
                listener.enterJoined_table(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitJoined_table"):
                listener.exitJoined_table(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitJoined_table"):
                return visitor.visitJoined_table(self)
            else:
                return visitor.visitChildren(self)




    def joined_table(self):

        localctx = ADQLParser.Joined_tableContext(self, self._ctx, self.state)
        self.enterRule(localctx, 120, self.RULE_joined_table)
        self._la = 0 # Token type
        try:
            self.state = 591
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,34,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 575
                self.table_reference(0)
                self.state = 577
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==ADQLParser.NATURAL:
                    self.state = 576
                    self.match(ADQLParser.NATURAL)


                self.state = 580
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if ((((_la - 135)) & ~0x3f) == 0 and ((1 << (_la - 135)) & ((1 << (ADQLParser.FULL - 135)) | (1 << (ADQLParser.INNER - 135)) | (1 << (ADQLParser.LEFT - 135)))) != 0) or _la==ADQLParser.RIGHT:
                    self.state = 579
                    self.join_type()


                self.state = 582
                self.match(ADQLParser.JOIN)
                self.state = 583
                self.table_reference(0)
                self.state = 585
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,33,self._ctx)
                if la_ == 1:
                    self.state = 584
                    self.join_specification()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 587
                self.match(ADQLParser.LPAREN)
                self.state = 588
                self.joined_table()
                self.state = 589
                self.match(ADQLParser.RPAREN)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Like_predicateContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Like_predicateContext, self).__init__(parent, invokingState)
            self.parser = parser

        def match_value(self):
            return self.getTypedRuleContext(ADQLParser.Match_valueContext,0)


        def LIKE(self):
            return self.getToken(ADQLParser.LIKE, 0)

        def pattern(self):
            return self.getTypedRuleContext(ADQLParser.PatternContext,0)


        def NOT(self):
            return self.getToken(ADQLParser.NOT, 0)

        def ILIKE(self):
            return self.getToken(ADQLParser.ILIKE, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_like_predicate

        def enterRule(self, listener):
            if hasattr(listener, "enterLike_predicate"):
                listener.enterLike_predicate(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitLike_predicate"):
                listener.exitLike_predicate(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitLike_predicate"):
                return visitor.visitLike_predicate(self)
            else:
                return visitor.visitChildren(self)




    def like_predicate(self):

        localctx = ADQLParser.Like_predicateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 122, self.RULE_like_predicate)
        self._la = 0 # Token type
        try:
            self.state = 607
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,37,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 593
                self.match_value()
                self.state = 595
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==ADQLParser.NOT:
                    self.state = 594
                    self.match(ADQLParser.NOT)


                self.state = 597
                self.match(ADQLParser.LIKE)
                self.state = 598
                self.pattern()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 600
                self.match_value()
                self.state = 602
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==ADQLParser.NOT:
                    self.state = 601
                    self.match(ADQLParser.NOT)


                self.state = 604
                self.match(ADQLParser.ILIKE)
                self.state = 605
                self.pattern()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Match_valueContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Match_valueContext, self).__init__(parent, invokingState)
            self.parser = parser

        def character_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Character_value_expressionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_match_value

        def enterRule(self, listener):
            if hasattr(listener, "enterMatch_value"):
                listener.enterMatch_value(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMatch_value"):
                listener.exitMatch_value(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitMatch_value"):
                return visitor.visitMatch_value(self)
            else:
                return visitor.visitChildren(self)




    def match_value(self):

        localctx = ADQLParser.Match_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 124, self.RULE_match_value)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 609
            self.character_value_expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Math_functionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Math_functionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ABS(self):
            return self.getToken(ADQLParser.ABS, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def numeric_value_expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Numeric_value_expressionContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Numeric_value_expressionContext,i)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def CEILING(self):
            return self.getToken(ADQLParser.CEILING, 0)

        def DEGREES(self):
            return self.getToken(ADQLParser.DEGREES, 0)

        def EXP(self):
            return self.getToken(ADQLParser.EXP, 0)

        def FLOOR(self):
            return self.getToken(ADQLParser.FLOOR, 0)

        def LOG(self):
            return self.getToken(ADQLParser.LOG, 0)

        def LOG10(self):
            return self.getToken(ADQLParser.LOG10, 0)

        def MOD(self):
            return self.getToken(ADQLParser.MOD, 0)

        def COMMA(self):
            return self.getToken(ADQLParser.COMMA, 0)

        def PI(self):
            return self.getToken(ADQLParser.PI, 0)

        def POWER(self):
            return self.getToken(ADQLParser.POWER, 0)

        def RADIANS(self):
            return self.getToken(ADQLParser.RADIANS, 0)

        def unsigned_decimal(self):
            return self.getTypedRuleContext(ADQLParser.Unsigned_decimalContext,0)


        def SQRT(self):
            return self.getToken(ADQLParser.SQRT, 0)

        def TRUNCATE(self):
            return self.getToken(ADQLParser.TRUNCATE, 0)

        def signed_integer(self):
            return self.getTypedRuleContext(ADQLParser.Signed_integerContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_math_function

        def enterRule(self, listener):
            if hasattr(listener, "enterMath_function"):
                listener.enterMath_function(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMath_function"):
                listener.exitMath_function(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitMath_function"):
                return visitor.visitMath_function(self)
            else:
                return visitor.visitChildren(self)




    def math_function(self):

        localctx = ADQLParser.Math_functionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 126, self.RULE_math_function)
        self._la = 0 # Token type
        try:
            self.state = 688
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,40,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 611
                self.match(ADQLParser.ABS)
                self.state = 612
                self.match(ADQLParser.LPAREN)
                self.state = 613
                self.numeric_value_expression(0)
                self.state = 614
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 616
                self.match(ADQLParser.CEILING)
                self.state = 617
                self.match(ADQLParser.LPAREN)
                self.state = 618
                self.numeric_value_expression(0)
                self.state = 619
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 621
                self.match(ADQLParser.DEGREES)
                self.state = 622
                self.match(ADQLParser.LPAREN)
                self.state = 623
                self.numeric_value_expression(0)
                self.state = 624
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 626
                self.match(ADQLParser.EXP)
                self.state = 627
                self.match(ADQLParser.LPAREN)
                self.state = 628
                self.numeric_value_expression(0)
                self.state = 629
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 631
                self.match(ADQLParser.FLOOR)
                self.state = 632
                self.match(ADQLParser.LPAREN)
                self.state = 633
                self.numeric_value_expression(0)
                self.state = 634
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 636
                self.match(ADQLParser.LOG)
                self.state = 637
                self.match(ADQLParser.LPAREN)
                self.state = 638
                self.numeric_value_expression(0)
                self.state = 639
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 641
                self.match(ADQLParser.LOG10)
                self.state = 642
                self.match(ADQLParser.LPAREN)
                self.state = 643
                self.numeric_value_expression(0)
                self.state = 644
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 646
                self.match(ADQLParser.MOD)
                self.state = 647
                self.match(ADQLParser.LPAREN)
                self.state = 648
                self.numeric_value_expression(0)
                self.state = 649
                self.match(ADQLParser.COMMA)
                self.state = 650
                self.numeric_value_expression(0)
                self.state = 651
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 653
                self.match(ADQLParser.PI)
                self.state = 654
                self.match(ADQLParser.LPAREN)
                self.state = 655
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 656
                self.match(ADQLParser.POWER)
                self.state = 657
                self.match(ADQLParser.LPAREN)
                self.state = 658
                self.numeric_value_expression(0)
                self.state = 659
                self.match(ADQLParser.COMMA)
                self.state = 660
                self.numeric_value_expression(0)
                self.state = 661
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 663
                self.match(ADQLParser.RADIANS)
                self.state = 664
                self.match(ADQLParser.LPAREN)
                self.state = 665
                self.numeric_value_expression(0)
                self.state = 666
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 668
                self.match(ADQLParser.RADIANS)
                self.state = 669
                self.match(ADQLParser.LPAREN)
                self.state = 671
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==ADQLParser.INT:
                    self.state = 670
                    self.unsigned_decimal()


                self.state = 673
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 13:
                self.enterOuterAlt(localctx, 13)
                self.state = 674
                self.match(ADQLParser.SQRT)
                self.state = 675
                self.match(ADQLParser.LPAREN)
                self.state = 676
                self.numeric_value_expression(0)
                self.state = 677
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 14:
                self.enterOuterAlt(localctx, 14)
                self.state = 679
                self.match(ADQLParser.TRUNCATE)
                self.state = 680
                self.match(ADQLParser.LPAREN)
                self.state = 681
                self.numeric_value_expression(0)
                self.state = 684
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==ADQLParser.COMMA:
                    self.state = 682
                    self.match(ADQLParser.COMMA)
                    self.state = 683
                    self.signed_integer()


                self.state = 686
                self.match(ADQLParser.RPAREN)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Named_columns_joinContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Named_columns_joinContext, self).__init__(parent, invokingState)
            self.parser = parser

        def USING(self):
            return self.getToken(ADQLParser.USING, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def join_column_list(self):
            return self.getTypedRuleContext(ADQLParser.Join_column_listContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_named_columns_join

        def enterRule(self, listener):
            if hasattr(listener, "enterNamed_columns_join"):
                listener.enterNamed_columns_join(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNamed_columns_join"):
                listener.exitNamed_columns_join(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitNamed_columns_join"):
                return visitor.visitNamed_columns_join(self)
            else:
                return visitor.visitChildren(self)




    def named_columns_join(self):

        localctx = ADQLParser.Named_columns_joinContext(self, self._ctx, self.state)
        self.enterRule(localctx, 128, self.RULE_named_columns_join)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 690
            self.match(ADQLParser.USING)
            self.state = 691
            self.match(ADQLParser.LPAREN)
            self.state = 692
            self.join_column_list()
            self.state = 693
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Non_join_query_expressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Non_join_query_expressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def non_join_query_term(self):
            return self.getTypedRuleContext(ADQLParser.Non_join_query_termContext,0)


        def query_expression(self):
            return self.getTypedRuleContext(ADQLParser.Query_expressionContext,0)


        def UNION(self):
            return self.getToken(ADQLParser.UNION, 0)

        def query_term(self):
            return self.getTypedRuleContext(ADQLParser.Query_termContext,0)


        def ALL(self):
            return self.getToken(ADQLParser.ALL, 0)

        def EXCEPT(self):
            return self.getToken(ADQLParser.EXCEPT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_non_join_query_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterNon_join_query_expression"):
                listener.enterNon_join_query_expression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNon_join_query_expression"):
                listener.exitNon_join_query_expression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitNon_join_query_expression"):
                return visitor.visitNon_join_query_expression(self)
            else:
                return visitor.visitChildren(self)




    def non_join_query_expression(self):

        localctx = ADQLParser.Non_join_query_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 130, self.RULE_non_join_query_expression)
        self._la = 0 # Token type
        try:
            self.state = 710
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,43,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 695
                self.non_join_query_term()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 696
                self.query_expression(0)
                self.state = 697
                self.match(ADQLParser.UNION)
                self.state = 699
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==ADQLParser.ALL:
                    self.state = 698
                    self.match(ADQLParser.ALL)


                self.state = 701
                self.query_term(0)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 703
                self.query_expression(0)
                self.state = 704
                self.match(ADQLParser.EXCEPT)
                self.state = 706
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==ADQLParser.ALL:
                    self.state = 705
                    self.match(ADQLParser.ALL)


                self.state = 708
                self.query_term(0)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Non_join_query_primaryContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Non_join_query_primaryContext, self).__init__(parent, invokingState)
            self.parser = parser

        def query_specification(self):
            return self.getTypedRuleContext(ADQLParser.Query_specificationContext,0)


        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def non_join_query_expression(self):
            return self.getTypedRuleContext(ADQLParser.Non_join_query_expressionContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_non_join_query_primary

        def enterRule(self, listener):
            if hasattr(listener, "enterNon_join_query_primary"):
                listener.enterNon_join_query_primary(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNon_join_query_primary"):
                listener.exitNon_join_query_primary(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitNon_join_query_primary"):
                return visitor.visitNon_join_query_primary(self)
            else:
                return visitor.visitChildren(self)




    def non_join_query_primary(self):

        localctx = ADQLParser.Non_join_query_primaryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 132, self.RULE_non_join_query_primary)
        try:
            self.state = 717
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.SELECT, ADQLParser.WITH]:
                self.enterOuterAlt(localctx, 1)
                self.state = 712
                self.query_specification()
                pass
            elif token in [ADQLParser.LPAREN]:
                self.enterOuterAlt(localctx, 2)
                self.state = 713
                self.match(ADQLParser.LPAREN)
                self.state = 714
                self.non_join_query_expression()
                self.state = 715
                self.match(ADQLParser.RPAREN)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Non_join_query_termContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Non_join_query_termContext, self).__init__(parent, invokingState)
            self.parser = parser

        def non_join_query_primary(self):
            return self.getTypedRuleContext(ADQLParser.Non_join_query_primaryContext,0)


        def query_term(self):
            return self.getTypedRuleContext(ADQLParser.Query_termContext,0)


        def INTERSECT(self):
            return self.getToken(ADQLParser.INTERSECT, 0)

        def query_expression(self):
            return self.getTypedRuleContext(ADQLParser.Query_expressionContext,0)


        def ALL(self):
            return self.getToken(ADQLParser.ALL, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_non_join_query_term

        def enterRule(self, listener):
            if hasattr(listener, "enterNon_join_query_term"):
                listener.enterNon_join_query_term(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNon_join_query_term"):
                listener.exitNon_join_query_term(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitNon_join_query_term"):
                return visitor.visitNon_join_query_term(self)
            else:
                return visitor.visitChildren(self)




    def non_join_query_term(self):

        localctx = ADQLParser.Non_join_query_termContext(self, self._ctx, self.state)
        self.enterRule(localctx, 134, self.RULE_non_join_query_term)
        self._la = 0 # Token type
        try:
            self.state = 727
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,46,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 719
                self.non_join_query_primary()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 720
                self.query_term(0)
                self.state = 721
                self.match(ADQLParser.INTERSECT)
                self.state = 723
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==ADQLParser.ALL:
                    self.state = 722
                    self.match(ADQLParser.ALL)


                self.state = 725
                self.query_expression(0)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Non_predicate_geometry_functionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Non_predicate_geometry_functionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def area(self):
            return self.getTypedRuleContext(ADQLParser.AreaContext,0)


        def coord1(self):
            return self.getTypedRuleContext(ADQLParser.Coord1Context,0)


        def coord2(self):
            return self.getTypedRuleContext(ADQLParser.Coord2Context,0)


        def distance(self):
            return self.getTypedRuleContext(ADQLParser.DistanceContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_non_predicate_geometry_function

        def enterRule(self, listener):
            if hasattr(listener, "enterNon_predicate_geometry_function"):
                listener.enterNon_predicate_geometry_function(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNon_predicate_geometry_function"):
                listener.exitNon_predicate_geometry_function(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitNon_predicate_geometry_function"):
                return visitor.visitNon_predicate_geometry_function(self)
            else:
                return visitor.visitChildren(self)




    def non_predicate_geometry_function(self):

        localctx = ADQLParser.Non_predicate_geometry_functionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 136, self.RULE_non_predicate_geometry_function)
        try:
            self.state = 733
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.AREA]:
                self.enterOuterAlt(localctx, 1)
                self.state = 729
                self.area()
                pass
            elif token in [ADQLParser.COORD1]:
                self.enterOuterAlt(localctx, 2)
                self.state = 730
                self.coord1()
                pass
            elif token in [ADQLParser.COORD2]:
                self.enterOuterAlt(localctx, 3)
                self.state = 731
                self.coord2()
                pass
            elif token in [ADQLParser.DISTANCE]:
                self.enterOuterAlt(localctx, 4)
                self.state = 732
                self.distance()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Null_predicateContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Null_predicateContext, self).__init__(parent, invokingState)
            self.parser = parser

        def column_reference(self):
            return self.getTypedRuleContext(ADQLParser.Column_referenceContext,0)


        def IS(self):
            return self.getToken(ADQLParser.IS, 0)

        def NULL(self):
            return self.getToken(ADQLParser.NULL, 0)

        def NOT(self):
            return self.getToken(ADQLParser.NOT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_null_predicate

        def enterRule(self, listener):
            if hasattr(listener, "enterNull_predicate"):
                listener.enterNull_predicate(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNull_predicate"):
                listener.exitNull_predicate(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitNull_predicate"):
                return visitor.visitNull_predicate(self)
            else:
                return visitor.visitChildren(self)




    def null_predicate(self):

        localctx = ADQLParser.Null_predicateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 138, self.RULE_null_predicate)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 735
            self.column_reference()
            self.state = 736
            self.match(ADQLParser.IS)
            self.state = 738
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.NOT:
                self.state = 737
                self.match(ADQLParser.NOT)


            self.state = 740
            self.match(ADQLParser.NULL)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Numeric_geometry_functionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Numeric_geometry_functionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def predicate_geometry_function(self):
            return self.getTypedRuleContext(ADQLParser.Predicate_geometry_functionContext,0)


        def non_predicate_geometry_function(self):
            return self.getTypedRuleContext(ADQLParser.Non_predicate_geometry_functionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_numeric_geometry_function

        def enterRule(self, listener):
            if hasattr(listener, "enterNumeric_geometry_function"):
                listener.enterNumeric_geometry_function(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNumeric_geometry_function"):
                listener.exitNumeric_geometry_function(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitNumeric_geometry_function"):
                return visitor.visitNumeric_geometry_function(self)
            else:
                return visitor.visitChildren(self)




    def numeric_geometry_function(self):

        localctx = ADQLParser.Numeric_geometry_functionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 140, self.RULE_numeric_geometry_function)
        try:
            self.state = 744
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.CONTAINS, ADQLParser.INTERSECTS]:
                self.enterOuterAlt(localctx, 1)
                self.state = 742
                self.predicate_geometry_function()
                pass
            elif token in [ADQLParser.AREA, ADQLParser.COORD1, ADQLParser.COORD2, ADQLParser.DISTANCE]:
                self.enterOuterAlt(localctx, 2)
                self.state = 743
                self.non_predicate_geometry_function()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Numeric_primaryContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Numeric_primaryContext, self).__init__(parent, invokingState)
            self.parser = parser

        def value_expression_primary(self):
            return self.getTypedRuleContext(ADQLParser.Value_expression_primaryContext,0)


        def sign(self):
            return self.getTypedRuleContext(ADQLParser.SignContext,0)


        def numeric_value_function(self):
            return self.getTypedRuleContext(ADQLParser.Numeric_value_functionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_numeric_primary

        def enterRule(self, listener):
            if hasattr(listener, "enterNumeric_primary"):
                listener.enterNumeric_primary(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNumeric_primary"):
                listener.exitNumeric_primary(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitNumeric_primary"):
                return visitor.visitNumeric_primary(self)
            else:
                return visitor.visitChildren(self)




    def numeric_primary(self):

        localctx = ADQLParser.Numeric_primaryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 142, self.RULE_numeric_primary)
        self._la = 0 # Token type
        try:
            self.state = 751
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,51,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 747
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==ADQLParser.PLUS or _la==ADQLParser.MINUS:
                    self.state = 746
                    self.sign()


                self.state = 749
                self.value_expression_primary()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 750
                self.numeric_value_function()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Numeric_value_expressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Numeric_value_expressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def term(self):
            return self.getTypedRuleContext(ADQLParser.TermContext,0)


        def bitwise_not(self):
            return self.getTypedRuleContext(ADQLParser.Bitwise_notContext,0)


        def numeric_value_expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Numeric_value_expressionContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Numeric_value_expressionContext,i)


        def bitwise_and(self):
            return self.getTypedRuleContext(ADQLParser.Bitwise_andContext,0)


        def bitwise_or(self):
            return self.getTypedRuleContext(ADQLParser.Bitwise_orContext,0)


        def bitwise_xor(self):
            return self.getTypedRuleContext(ADQLParser.Bitwise_xorContext,0)


        def PLUS(self):
            return self.getToken(ADQLParser.PLUS, 0)

        def MINUS(self):
            return self.getToken(ADQLParser.MINUS, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_numeric_value_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterNumeric_value_expression"):
                listener.enterNumeric_value_expression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNumeric_value_expression"):
                listener.exitNumeric_value_expression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitNumeric_value_expression"):
                return visitor.visitNumeric_value_expression(self)
            else:
                return visitor.visitChildren(self)



    def numeric_value_expression(self, _p=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ADQLParser.Numeric_value_expressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 144
        self.enterRecursionRule(localctx, 144, self.RULE_numeric_value_expression, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 758
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.ABS, ADQLParser.ACOS, ADQLParser.AREA, ADQLParser.ASIN, ADQLParser.ATAN, ADQLParser.ATAN2, ADQLParser.CEILING, ADQLParser.CONTAINS, ADQLParser.COORD1, ADQLParser.COORD2, ADQLParser.COS, ADQLParser.COT, ADQLParser.DEGREES, ADQLParser.DISTANCE, ADQLParser.EXP, ADQLParser.FLOOR, ADQLParser.INTERSECTS, ADQLParser.LOG, ADQLParser.LOG10, ADQLParser.MOD, ADQLParser.PI, ADQLParser.POWER, ADQLParser.RADIANS, ADQLParser.SIN, ADQLParser.SQRT, ADQLParser.TAN, ADQLParser.TRUNCATE, ADQLParser.AVG, ADQLParser.COUNT, ADQLParser.MAX, ADQLParser.MIN, ADQLParser.SUM, ADQLParser.INT, ADQLParser.REAL, ADQLParser.HEX_DIGIT, ADQLParser.ID, ADQLParser.LPAREN, ADQLParser.PLUS, ADQLParser.MINUS, ADQLParser.DOT, ADQLParser.DQ, ADQLParser.SQ]:
                self.state = 754
                self.term(0)
                pass
            elif token in [ADQLParser.TILDE]:
                self.state = 755
                self.bitwise_not()
                self.state = 756
                self.numeric_value_expression(6)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 780
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,54,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 778
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,53,self._ctx)
                    if la_ == 1:
                        localctx = ADQLParser.Numeric_value_expressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_numeric_value_expression)
                        self.state = 760
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 761
                        self.bitwise_and()
                        self.state = 762
                        self.numeric_value_expression(6)
                        pass

                    elif la_ == 2:
                        localctx = ADQLParser.Numeric_value_expressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_numeric_value_expression)
                        self.state = 764
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 765
                        self.bitwise_or()
                        self.state = 766
                        self.numeric_value_expression(5)
                        pass

                    elif la_ == 3:
                        localctx = ADQLParser.Numeric_value_expressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_numeric_value_expression)
                        self.state = 768
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 769
                        self.bitwise_xor()
                        self.state = 770
                        self.numeric_value_expression(4)
                        pass

                    elif la_ == 4:
                        localctx = ADQLParser.Numeric_value_expressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_numeric_value_expression)
                        self.state = 772
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 773
                        self.match(ADQLParser.PLUS)
                        self.state = 774
                        self.term(0)
                        pass

                    elif la_ == 5:
                        localctx = ADQLParser.Numeric_value_expressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_numeric_value_expression)
                        self.state = 775
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 776
                        self.match(ADQLParser.MINUS)
                        self.state = 777
                        self.term(0)
                        pass

             
                self.state = 782
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,54,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class Numeric_value_functionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Numeric_value_functionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def trig_function(self):
            return self.getTypedRuleContext(ADQLParser.Trig_functionContext,0)


        def math_function(self):
            return self.getTypedRuleContext(ADQLParser.Math_functionContext,0)


        def numeric_geometry_function(self):
            return self.getTypedRuleContext(ADQLParser.Numeric_geometry_functionContext,0)


        def user_defined_function(self):
            return self.getTypedRuleContext(ADQLParser.User_defined_functionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_numeric_value_function

        def enterRule(self, listener):
            if hasattr(listener, "enterNumeric_value_function"):
                listener.enterNumeric_value_function(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitNumeric_value_function"):
                listener.exitNumeric_value_function(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitNumeric_value_function"):
                return visitor.visitNumeric_value_function(self)
            else:
                return visitor.visitChildren(self)




    def numeric_value_function(self):

        localctx = ADQLParser.Numeric_value_functionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 146, self.RULE_numeric_value_function)
        try:
            self.state = 787
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.ACOS, ADQLParser.ASIN, ADQLParser.ATAN, ADQLParser.ATAN2, ADQLParser.COS, ADQLParser.COT, ADQLParser.SIN, ADQLParser.TAN]:
                self.enterOuterAlt(localctx, 1)
                self.state = 783
                self.trig_function()
                pass
            elif token in [ADQLParser.ABS, ADQLParser.CEILING, ADQLParser.DEGREES, ADQLParser.EXP, ADQLParser.FLOOR, ADQLParser.LOG, ADQLParser.LOG10, ADQLParser.MOD, ADQLParser.PI, ADQLParser.POWER, ADQLParser.RADIANS, ADQLParser.SQRT, ADQLParser.TRUNCATE]:
                self.enterOuterAlt(localctx, 2)
                self.state = 784
                self.math_function()
                pass
            elif token in [ADQLParser.AREA, ADQLParser.CONTAINS, ADQLParser.COORD1, ADQLParser.COORD2, ADQLParser.DISTANCE, ADQLParser.INTERSECTS]:
                self.enterOuterAlt(localctx, 3)
                self.state = 785
                self.numeric_geometry_function()
                pass
            elif token in [ADQLParser.ID]:
                self.enterOuterAlt(localctx, 4)
                self.state = 786
                self.user_defined_function()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Offset_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Offset_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def OFFSET(self):
            return self.getToken(ADQLParser.OFFSET, 0)

        def unsigned_decimal(self):
            return self.getTypedRuleContext(ADQLParser.Unsigned_decimalContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_offset_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterOffset_clause"):
                listener.enterOffset_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOffset_clause"):
                listener.exitOffset_clause(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitOffset_clause"):
                return visitor.visitOffset_clause(self)
            else:
                return visitor.visitChildren(self)




    def offset_clause(self):

        localctx = ADQLParser.Offset_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 148, self.RULE_offset_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 789
            self.match(ADQLParser.OFFSET)
            self.state = 790
            self.unsigned_decimal()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Order_by_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Order_by_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ORDER(self):
            return self.getToken(ADQLParser.ORDER, 0)

        def BY(self):
            return self.getToken(ADQLParser.BY, 0)

        def sort_specification_list(self):
            return self.getTypedRuleContext(ADQLParser.Sort_specification_listContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_order_by_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterOrder_by_clause"):
                listener.enterOrder_by_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOrder_by_clause"):
                listener.exitOrder_by_clause(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitOrder_by_clause"):
                return visitor.visitOrder_by_clause(self)
            else:
                return visitor.visitChildren(self)




    def order_by_clause(self):

        localctx = ADQLParser.Order_by_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 150, self.RULE_order_by_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 792
            self.match(ADQLParser.ORDER)
            self.state = 793
            self.match(ADQLParser.BY)
            self.state = 794
            self.sort_specification_list()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Ordering_specificationContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Ordering_specificationContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ASC(self):
            return self.getToken(ADQLParser.ASC, 0)

        def DESC(self):
            return self.getToken(ADQLParser.DESC, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_ordering_specification

        def enterRule(self, listener):
            if hasattr(listener, "enterOrdering_specification"):
                listener.enterOrdering_specification(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOrdering_specification"):
                listener.exitOrdering_specification(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitOrdering_specification"):
                return visitor.visitOrdering_specification(self)
            else:
                return visitor.visitChildren(self)




    def ordering_specification(self):

        localctx = ADQLParser.Ordering_specificationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 152, self.RULE_ordering_specification)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 796
            _la = self._input.LA(1)
            if not(_la==ADQLParser.ASC or _la==ADQLParser.DESC):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Outer_join_typeContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Outer_join_typeContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LEFT(self):
            return self.getToken(ADQLParser.LEFT, 0)

        def RIGHT(self):
            return self.getToken(ADQLParser.RIGHT, 0)

        def FULL(self):
            return self.getToken(ADQLParser.FULL, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_outer_join_type

        def enterRule(self, listener):
            if hasattr(listener, "enterOuter_join_type"):
                listener.enterOuter_join_type(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitOuter_join_type"):
                listener.exitOuter_join_type(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitOuter_join_type"):
                return visitor.visitOuter_join_type(self)
            else:
                return visitor.visitChildren(self)




    def outer_join_type(self):

        localctx = ADQLParser.Outer_join_typeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 154, self.RULE_outer_join_type)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 798
            _la = self._input.LA(1)
            if not(_la==ADQLParser.FULL or _la==ADQLParser.LEFT or _la==ADQLParser.RIGHT):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PatternContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.PatternContext, self).__init__(parent, invokingState)
            self.parser = parser

        def character_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Character_value_expressionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_pattern

        def enterRule(self, listener):
            if hasattr(listener, "enterPattern"):
                listener.enterPattern(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPattern"):
                listener.exitPattern(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitPattern"):
                return visitor.visitPattern(self)
            else:
                return visitor.visitChildren(self)




    def pattern(self):

        localctx = ADQLParser.PatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 156, self.RULE_pattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 800
            self.character_value_expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PointContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.PointContext, self).__init__(parent, invokingState)
            self.parser = parser

        def POINT(self):
            return self.getToken(ADQLParser.POINT, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def coord_sys(self):
            return self.getTypedRuleContext(ADQLParser.Coord_sysContext,0)


        def COMMA(self):
            return self.getToken(ADQLParser.COMMA, 0)

        def coordinates(self):
            return self.getTypedRuleContext(ADQLParser.CoordinatesContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_point

        def enterRule(self, listener):
            if hasattr(listener, "enterPoint"):
                listener.enterPoint(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPoint"):
                listener.exitPoint(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitPoint"):
                return visitor.visitPoint(self)
            else:
                return visitor.visitChildren(self)




    def point(self):

        localctx = ADQLParser.PointContext(self, self._ctx, self.state)
        self.enterRule(localctx, 158, self.RULE_point)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 802
            self.match(ADQLParser.POINT)
            self.state = 803
            self.match(ADQLParser.LPAREN)
            self.state = 804
            self.coord_sys()
            self.state = 805
            self.match(ADQLParser.COMMA)
            self.state = 806
            self.coordinates()
            self.state = 807
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PolygonContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.PolygonContext, self).__init__(parent, invokingState)
            self.parser = parser

        def POLYGON(self):
            return self.getToken(ADQLParser.POLYGON, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def coord_sys(self):
            return self.getTypedRuleContext(ADQLParser.Coord_sysContext,0)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.COMMA)
            else:
                return self.getToken(ADQLParser.COMMA, i)

        def coordinates(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.CoordinatesContext)
            else:
                return self.getTypedRuleContext(ADQLParser.CoordinatesContext,i)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_polygon

        def enterRule(self, listener):
            if hasattr(listener, "enterPolygon"):
                listener.enterPolygon(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPolygon"):
                listener.exitPolygon(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitPolygon"):
                return visitor.visitPolygon(self)
            else:
                return visitor.visitChildren(self)




    def polygon(self):

        localctx = ADQLParser.PolygonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 160, self.RULE_polygon)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 809
            self.match(ADQLParser.POLYGON)
            self.state = 810
            self.match(ADQLParser.LPAREN)
            self.state = 811
            self.coord_sys()
            self.state = 812
            self.match(ADQLParser.COMMA)
            self.state = 813
            self.coordinates()
            self.state = 814
            self.match(ADQLParser.COMMA)
            self.state = 815
            self.coordinates()
            self.state = 818 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 816
                self.match(ADQLParser.COMMA)
                self.state = 817
                self.coordinates()
                self.state = 820 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==ADQLParser.COMMA):
                    break

            self.state = 822
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PredicateContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.PredicateContext, self).__init__(parent, invokingState)
            self.parser = parser

        def comparison_predicate(self):
            return self.getTypedRuleContext(ADQLParser.Comparison_predicateContext,0)


        def between_predicate(self):
            return self.getTypedRuleContext(ADQLParser.Between_predicateContext,0)


        def in_predicate(self):
            return self.getTypedRuleContext(ADQLParser.In_predicateContext,0)


        def like_predicate(self):
            return self.getTypedRuleContext(ADQLParser.Like_predicateContext,0)


        def null_predicate(self):
            return self.getTypedRuleContext(ADQLParser.Null_predicateContext,0)


        def exists_predicate(self):
            return self.getTypedRuleContext(ADQLParser.Exists_predicateContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_predicate

        def enterRule(self, listener):
            if hasattr(listener, "enterPredicate"):
                listener.enterPredicate(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPredicate"):
                listener.exitPredicate(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitPredicate"):
                return visitor.visitPredicate(self)
            else:
                return visitor.visitChildren(self)




    def predicate(self):

        localctx = ADQLParser.PredicateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 162, self.RULE_predicate)
        try:
            self.state = 830
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,57,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 824
                self.comparison_predicate()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 825
                self.between_predicate()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 826
                self.in_predicate()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 827
                self.like_predicate()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 828
                self.null_predicate()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 829
                self.exists_predicate()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Predicate_geometry_functionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Predicate_geometry_functionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def contains(self):
            return self.getTypedRuleContext(ADQLParser.ContainsContext,0)


        def intersects(self):
            return self.getTypedRuleContext(ADQLParser.IntersectsContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_predicate_geometry_function

        def enterRule(self, listener):
            if hasattr(listener, "enterPredicate_geometry_function"):
                listener.enterPredicate_geometry_function(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitPredicate_geometry_function"):
                listener.exitPredicate_geometry_function(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitPredicate_geometry_function"):
                return visitor.visitPredicate_geometry_function(self)
            else:
                return visitor.visitChildren(self)




    def predicate_geometry_function(self):

        localctx = ADQLParser.Predicate_geometry_functionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 164, self.RULE_predicate_geometry_function)
        try:
            self.state = 834
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.CONTAINS]:
                self.enterOuterAlt(localctx, 1)
                self.state = 832
                self.contains()
                pass
            elif token in [ADQLParser.INTERSECTS]:
                self.enterOuterAlt(localctx, 2)
                self.state = 833
                self.intersects()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class QualifierContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.QualifierContext, self).__init__(parent, invokingState)
            self.parser = parser

        def column_name(self):
            return self.getTypedRuleContext(ADQLParser.Column_nameContext,0)


        def table_name(self):
            return self.getTypedRuleContext(ADQLParser.Table_nameContext,0)


        def correlation_name(self):
            return self.getTypedRuleContext(ADQLParser.Correlation_nameContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_qualifier

        def enterRule(self, listener):
            if hasattr(listener, "enterQualifier"):
                listener.enterQualifier(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitQualifier"):
                listener.exitQualifier(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitQualifier"):
                return visitor.visitQualifier(self)
            else:
                return visitor.visitChildren(self)




    def qualifier(self):

        localctx = ADQLParser.QualifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 166, self.RULE_qualifier)
        try:
            self.state = 839
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,59,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 836
                self.column_name()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 837
                self.table_name()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 838
                self.correlation_name()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Query_expressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Query_expressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def non_join_query_term(self):
            return self.getTypedRuleContext(ADQLParser.Non_join_query_termContext,0)


        def joined_table(self):
            return self.getTypedRuleContext(ADQLParser.Joined_tableContext,0)


        def query_expression(self):
            return self.getTypedRuleContext(ADQLParser.Query_expressionContext,0)


        def UNION(self):
            return self.getToken(ADQLParser.UNION, 0)

        def query_term(self):
            return self.getTypedRuleContext(ADQLParser.Query_termContext,0)


        def ALL(self):
            return self.getToken(ADQLParser.ALL, 0)

        def EXCEPT(self):
            return self.getToken(ADQLParser.EXCEPT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_query_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterQuery_expression"):
                listener.enterQuery_expression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitQuery_expression"):
                listener.exitQuery_expression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitQuery_expression"):
                return visitor.visitQuery_expression(self)
            else:
                return visitor.visitChildren(self)



    def query_expression(self, _p=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ADQLParser.Query_expressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 168
        self.enterRecursionRule(localctx, 168, self.RULE_query_expression, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 844
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,60,self._ctx)
            if la_ == 1:
                self.state = 842
                self.non_join_query_term()
                pass

            elif la_ == 2:
                self.state = 843
                self.joined_table()
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 860
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,64,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 858
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,63,self._ctx)
                    if la_ == 1:
                        localctx = ADQLParser.Query_expressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_query_expression)
                        self.state = 846
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 847
                        self.match(ADQLParser.UNION)
                        self.state = 849
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==ADQLParser.ALL:
                            self.state = 848
                            self.match(ADQLParser.ALL)


                        self.state = 851
                        self.query_term(0)
                        pass

                    elif la_ == 2:
                        localctx = ADQLParser.Query_expressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_query_expression)
                        self.state = 852
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 853
                        self.match(ADQLParser.EXCEPT)
                        self.state = 855
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==ADQLParser.ALL:
                            self.state = 854
                            self.match(ADQLParser.ALL)


                        self.state = 857
                        self.query_term(0)
                        pass

             
                self.state = 862
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,64,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class Query_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Query_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(ADQLParser.ID, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_query_name

        def enterRule(self, listener):
            if hasattr(listener, "enterQuery_name"):
                listener.enterQuery_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitQuery_name"):
                listener.exitQuery_name(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitQuery_name"):
                return visitor.visitQuery_name(self)
            else:
                return visitor.visitChildren(self)




    def query_name(self):

        localctx = ADQLParser.Query_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 170, self.RULE_query_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 863
            self.match(ADQLParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Query_specificationContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Query_specificationContext, self).__init__(parent, invokingState)
            self.parser = parser

        def select_query(self):
            return self.getTypedRuleContext(ADQLParser.Select_queryContext,0)


        def SEMI(self):
            return self.getToken(ADQLParser.SEMI, 0)

        def WITH(self):
            return self.getToken(ADQLParser.WITH, 0)

        def with_query(self):
            return self.getTypedRuleContext(ADQLParser.With_queryContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_query_specification

        def enterRule(self, listener):
            if hasattr(listener, "enterQuery_specification"):
                listener.enterQuery_specification(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitQuery_specification"):
                listener.exitQuery_specification(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitQuery_specification"):
                return visitor.visitQuery_specification(self)
            else:
                return visitor.visitChildren(self)




    def query_specification(self):

        localctx = ADQLParser.Query_specificationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 172, self.RULE_query_specification)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 867
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.WITH:
                self.state = 865
                self.match(ADQLParser.WITH)
                self.state = 866
                self.with_query()


            self.state = 869
            self.select_query()
            self.state = 870
            self.match(ADQLParser.SEMI)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Query_termContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Query_termContext, self).__init__(parent, invokingState)
            self.parser = parser

        def non_join_query_primary(self):
            return self.getTypedRuleContext(ADQLParser.Non_join_query_primaryContext,0)


        def joined_table(self):
            return self.getTypedRuleContext(ADQLParser.Joined_tableContext,0)


        def query_term(self):
            return self.getTypedRuleContext(ADQLParser.Query_termContext,0)


        def INTERSECT(self):
            return self.getToken(ADQLParser.INTERSECT, 0)

        def query_expression(self):
            return self.getTypedRuleContext(ADQLParser.Query_expressionContext,0)


        def ALL(self):
            return self.getToken(ADQLParser.ALL, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_query_term

        def enterRule(self, listener):
            if hasattr(listener, "enterQuery_term"):
                listener.enterQuery_term(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitQuery_term"):
                listener.exitQuery_term(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitQuery_term"):
                return visitor.visitQuery_term(self)
            else:
                return visitor.visitChildren(self)



    def query_term(self, _p=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ADQLParser.Query_termContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 174
        self.enterRecursionRule(localctx, 174, self.RULE_query_term, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 875
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,66,self._ctx)
            if la_ == 1:
                self.state = 873
                self.non_join_query_primary()
                pass

            elif la_ == 2:
                self.state = 874
                self.joined_table()
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 885
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,68,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = ADQLParser.Query_termContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_query_term)
                    self.state = 877
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 878
                    self.match(ADQLParser.INTERSECT)
                    self.state = 880
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==ADQLParser.ALL:
                        self.state = 879
                        self.match(ADQLParser.ALL)


                    self.state = 882
                    self.query_expression(0) 
                self.state = 887
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,68,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class RadiusContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.RadiusContext, self).__init__(parent, invokingState)
            self.parser = parser

        def numeric_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Numeric_value_expressionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_radius

        def enterRule(self, listener):
            if hasattr(listener, "enterRadius"):
                listener.enterRadius(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitRadius"):
                listener.exitRadius(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitRadius"):
                return visitor.visitRadius(self)
            else:
                return visitor.visitChildren(self)




    def radius(self):

        localctx = ADQLParser.RadiusContext(self, self._ctx, self.state)
        self.enterRule(localctx, 176, self.RULE_radius)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 888
            self.numeric_value_expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class RegionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.RegionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def REGION(self):
            return self.getToken(ADQLParser.REGION, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def string_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.String_value_expressionContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_region

        def enterRule(self, listener):
            if hasattr(listener, "enterRegion"):
                listener.enterRegion(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitRegion"):
                listener.exitRegion(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitRegion"):
                return visitor.visitRegion(self)
            else:
                return visitor.visitChildren(self)




    def region(self):

        localctx = ADQLParser.RegionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 178, self.RULE_region)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 890
            self.match(ADQLParser.REGION)
            self.state = 891
            self.match(ADQLParser.LPAREN)
            self.state = 892
            self.string_value_expression()
            self.state = 893
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Regular_identifierContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Regular_identifierContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(ADQLParser.ID, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_regular_identifier

        def enterRule(self, listener):
            if hasattr(listener, "enterRegular_identifier"):
                listener.enterRegular_identifier(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitRegular_identifier"):
                listener.exitRegular_identifier(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitRegular_identifier"):
                return visitor.visitRegular_identifier(self)
            else:
                return visitor.visitChildren(self)




    def regular_identifier(self):

        localctx = ADQLParser.Regular_identifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 180, self.RULE_regular_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 895
            self.match(ADQLParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Schema_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Schema_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(ADQLParser.ID, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_schema_name

        def enterRule(self, listener):
            if hasattr(listener, "enterSchema_name"):
                listener.enterSchema_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSchema_name"):
                listener.exitSchema_name(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSchema_name"):
                return visitor.visitSchema_name(self)
            else:
                return visitor.visitChildren(self)




    def schema_name(self):

        localctx = ADQLParser.Schema_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 182, self.RULE_schema_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 897
            self.match(ADQLParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Search_conditionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Search_conditionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def boolean_term(self):
            return self.getTypedRuleContext(ADQLParser.Boolean_termContext,0)


        def search_condition(self):
            return self.getTypedRuleContext(ADQLParser.Search_conditionContext,0)


        def OR(self):
            return self.getToken(ADQLParser.OR, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_search_condition

        def enterRule(self, listener):
            if hasattr(listener, "enterSearch_condition"):
                listener.enterSearch_condition(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSearch_condition"):
                listener.exitSearch_condition(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSearch_condition"):
                return visitor.visitSearch_condition(self)
            else:
                return visitor.visitChildren(self)



    def search_condition(self, _p=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ADQLParser.Search_conditionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 184
        self.enterRecursionRule(localctx, 184, self.RULE_search_condition, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 900
            self.boolean_term(0)
            self._ctx.stop = self._input.LT(-1)
            self.state = 907
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,69,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = ADQLParser.Search_conditionContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_search_condition)
                    self.state = 902
                    if not self.precpred(self._ctx, 1):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                    self.state = 903
                    self.match(ADQLParser.OR)
                    self.state = 904
                    self.boolean_term(0) 
                self.state = 909
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,69,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class Select_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Select_listContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ASTERISK(self):
            return self.getToken(ADQLParser.ASTERISK, 0)

        def select_sublist(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Select_sublistContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Select_sublistContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.COMMA)
            else:
                return self.getToken(ADQLParser.COMMA, i)

        def getRuleIndex(self):
            return ADQLParser.RULE_select_list

        def enterRule(self, listener):
            if hasattr(listener, "enterSelect_list"):
                listener.enterSelect_list(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSelect_list"):
                listener.exitSelect_list(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSelect_list"):
                return visitor.visitSelect_list(self)
            else:
                return visitor.visitChildren(self)




    def select_list(self):

        localctx = ADQLParser.Select_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 186, self.RULE_select_list)
        self._la = 0 # Token type
        try:
            self.state = 919
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.ASTERISK]:
                self.enterOuterAlt(localctx, 1)
                self.state = 910
                self.match(ADQLParser.ASTERISK)
                pass
            elif token in [ADQLParser.ABS, ADQLParser.ACOS, ADQLParser.AREA, ADQLParser.ASIN, ADQLParser.ATAN, ADQLParser.ATAN2, ADQLParser.BOX, ADQLParser.CEILING, ADQLParser.CENTROID, ADQLParser.CIRCLE, ADQLParser.CONTAINS, ADQLParser.COORD1, ADQLParser.COORD2, ADQLParser.COORDSYS, ADQLParser.COS, ADQLParser.COT, ADQLParser.DEGREES, ADQLParser.DISTANCE, ADQLParser.EXP, ADQLParser.FLOOR, ADQLParser.INTERSECTS, ADQLParser.LOG, ADQLParser.LOG10, ADQLParser.MOD, ADQLParser.PI, ADQLParser.POINT, ADQLParser.POLYGON, ADQLParser.POWER, ADQLParser.RADIANS, ADQLParser.REGION, ADQLParser.SIN, ADQLParser.SQRT, ADQLParser.TAN, ADQLParser.TRUNCATE, ADQLParser.AVG, ADQLParser.COUNT, ADQLParser.FALSE, ADQLParser.MAX, ADQLParser.MIN, ADQLParser.SUM, ADQLParser.TRUE, ADQLParser.INT, ADQLParser.REAL, ADQLParser.HEX_DIGIT, ADQLParser.ID, ADQLParser.TILDE, ADQLParser.LPAREN, ADQLParser.PLUS, ADQLParser.MINUS, ADQLParser.DOT, ADQLParser.DQ, ADQLParser.SQ]:
                self.enterOuterAlt(localctx, 2)
                self.state = 911
                self.select_sublist()
                self.state = 916
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==ADQLParser.COMMA:
                    self.state = 912
                    self.match(ADQLParser.COMMA)
                    self.state = 913
                    self.select_sublist()
                    self.state = 918
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Select_queryContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Select_queryContext, self).__init__(parent, invokingState)
            self.parser = parser

        def SELECT(self):
            return self.getToken(ADQLParser.SELECT, 0)

        def select_list(self):
            return self.getTypedRuleContext(ADQLParser.Select_listContext,0)


        def table_expression(self):
            return self.getTypedRuleContext(ADQLParser.Table_expressionContext,0)


        def set_quantifier(self):
            return self.getTypedRuleContext(ADQLParser.Set_quantifierContext,0)


        def set_limit(self):
            return self.getTypedRuleContext(ADQLParser.Set_limitContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_select_query

        def enterRule(self, listener):
            if hasattr(listener, "enterSelect_query"):
                listener.enterSelect_query(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSelect_query"):
                listener.exitSelect_query(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSelect_query"):
                return visitor.visitSelect_query(self)
            else:
                return visitor.visitChildren(self)




    def select_query(self):

        localctx = ADQLParser.Select_queryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 188, self.RULE_select_query)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 921
            self.match(ADQLParser.SELECT)
            self.state = 923
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.ALL or _la==ADQLParser.DISTINCT:
                self.state = 922
                self.set_quantifier()


            self.state = 926
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.TOP:
                self.state = 925
                self.set_limit()


            self.state = 928
            self.select_list()
            self.state = 929
            self.table_expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Select_sublistContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Select_sublistContext, self).__init__(parent, invokingState)
            self.parser = parser

        def derived_column(self):
            return self.getTypedRuleContext(ADQLParser.Derived_columnContext,0)


        def qualifier(self):
            return self.getTypedRuleContext(ADQLParser.QualifierContext,0)


        def DOT(self):
            return self.getToken(ADQLParser.DOT, 0)

        def ASTERISK(self):
            return self.getToken(ADQLParser.ASTERISK, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_select_sublist

        def enterRule(self, listener):
            if hasattr(listener, "enterSelect_sublist"):
                listener.enterSelect_sublist(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSelect_sublist"):
                listener.exitSelect_sublist(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSelect_sublist"):
                return visitor.visitSelect_sublist(self)
            else:
                return visitor.visitChildren(self)




    def select_sublist(self):

        localctx = ADQLParser.Select_sublistContext(self, self._ctx, self.state)
        self.enterRule(localctx, 190, self.RULE_select_sublist)
        try:
            self.state = 936
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,74,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 931
                self.derived_column()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 932
                self.qualifier()
                self.state = 933
                self.match(ADQLParser.DOT)
                self.state = 934
                self.match(ADQLParser.ASTERISK)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Set_function_specificationContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Set_function_specificationContext, self).__init__(parent, invokingState)
            self.parser = parser

        def COUNT(self):
            return self.getToken(ADQLParser.COUNT, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def ASTERISK(self):
            return self.getToken(ADQLParser.ASTERISK, 0)

        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def general_set_function(self):
            return self.getTypedRuleContext(ADQLParser.General_set_functionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_set_function_specification

        def enterRule(self, listener):
            if hasattr(listener, "enterSet_function_specification"):
                listener.enterSet_function_specification(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSet_function_specification"):
                listener.exitSet_function_specification(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSet_function_specification"):
                return visitor.visitSet_function_specification(self)
            else:
                return visitor.visitChildren(self)




    def set_function_specification(self):

        localctx = ADQLParser.Set_function_specificationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 192, self.RULE_set_function_specification)
        try:
            self.state = 943
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,75,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 938
                self.match(ADQLParser.COUNT)
                self.state = 939
                self.match(ADQLParser.LPAREN)
                self.state = 940
                self.match(ADQLParser.ASTERISK)
                self.state = 941
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 942
                self.general_set_function()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Set_function_typeContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Set_function_typeContext, self).__init__(parent, invokingState)
            self.parser = parser

        def AVG(self):
            return self.getToken(ADQLParser.AVG, 0)

        def MAX(self):
            return self.getToken(ADQLParser.MAX, 0)

        def MIN(self):
            return self.getToken(ADQLParser.MIN, 0)

        def SUM(self):
            return self.getToken(ADQLParser.SUM, 0)

        def COUNT(self):
            return self.getToken(ADQLParser.COUNT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_set_function_type

        def enterRule(self, listener):
            if hasattr(listener, "enterSet_function_type"):
                listener.enterSet_function_type(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSet_function_type"):
                listener.exitSet_function_type(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSet_function_type"):
                return visitor.visitSet_function_type(self)
            else:
                return visitor.visitChildren(self)




    def set_function_type(self):

        localctx = ADQLParser.Set_function_typeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 194, self.RULE_set_function_type)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 945
            _la = self._input.LA(1)
            if not(_la==ADQLParser.AVG or _la==ADQLParser.COUNT or _la==ADQLParser.MAX or _la==ADQLParser.MIN or _la==ADQLParser.SUM):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Set_limitContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Set_limitContext, self).__init__(parent, invokingState)
            self.parser = parser

        def TOP(self):
            return self.getToken(ADQLParser.TOP, 0)

        def unsigned_decimal(self):
            return self.getTypedRuleContext(ADQLParser.Unsigned_decimalContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_set_limit

        def enterRule(self, listener):
            if hasattr(listener, "enterSet_limit"):
                listener.enterSet_limit(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSet_limit"):
                listener.exitSet_limit(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSet_limit"):
                return visitor.visitSet_limit(self)
            else:
                return visitor.visitChildren(self)




    def set_limit(self):

        localctx = ADQLParser.Set_limitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 196, self.RULE_set_limit)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 947
            self.match(ADQLParser.TOP)
            self.state = 948
            self.unsigned_decimal()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Set_quantifierContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Set_quantifierContext, self).__init__(parent, invokingState)
            self.parser = parser

        def DISTINCT(self):
            return self.getToken(ADQLParser.DISTINCT, 0)

        def ALL(self):
            return self.getToken(ADQLParser.ALL, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_set_quantifier

        def enterRule(self, listener):
            if hasattr(listener, "enterSet_quantifier"):
                listener.enterSet_quantifier(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSet_quantifier"):
                listener.exitSet_quantifier(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSet_quantifier"):
                return visitor.visitSet_quantifier(self)
            else:
                return visitor.visitChildren(self)




    def set_quantifier(self):

        localctx = ADQLParser.Set_quantifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 198, self.RULE_set_quantifier)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 950
            _la = self._input.LA(1)
            if not(_la==ADQLParser.ALL or _la==ADQLParser.DISTINCT):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class SignContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.SignContext, self).__init__(parent, invokingState)
            self.parser = parser

        def PLUS(self):
            return self.getToken(ADQLParser.PLUS, 0)

        def MINUS(self):
            return self.getToken(ADQLParser.MINUS, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_sign

        def enterRule(self, listener):
            if hasattr(listener, "enterSign"):
                listener.enterSign(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSign"):
                listener.exitSign(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSign"):
                return visitor.visitSign(self)
            else:
                return visitor.visitChildren(self)




    def sign(self):

        localctx = ADQLParser.SignContext(self, self._ctx, self.state)
        self.enterRule(localctx, 200, self.RULE_sign)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 952
            _la = self._input.LA(1)
            if not(_la==ADQLParser.PLUS or _la==ADQLParser.MINUS):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Signed_integerContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Signed_integerContext, self).__init__(parent, invokingState)
            self.parser = parser

        def unsigned_decimal(self):
            return self.getTypedRuleContext(ADQLParser.Unsigned_decimalContext,0)


        def sign(self):
            return self.getTypedRuleContext(ADQLParser.SignContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_signed_integer

        def enterRule(self, listener):
            if hasattr(listener, "enterSigned_integer"):
                listener.enterSigned_integer(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSigned_integer"):
                listener.exitSigned_integer(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSigned_integer"):
                return visitor.visitSigned_integer(self)
            else:
                return visitor.visitChildren(self)




    def signed_integer(self):

        localctx = ADQLParser.Signed_integerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 202, self.RULE_signed_integer)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 955
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.PLUS or _la==ADQLParser.MINUS:
                self.state = 954
                self.sign()


            self.state = 957
            self.unsigned_decimal()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Sort_keyContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Sort_keyContext, self).__init__(parent, invokingState)
            self.parser = parser

        def column_name(self):
            return self.getTypedRuleContext(ADQLParser.Column_nameContext,0)


        def unsigned_decimal(self):
            return self.getTypedRuleContext(ADQLParser.Unsigned_decimalContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_sort_key

        def enterRule(self, listener):
            if hasattr(listener, "enterSort_key"):
                listener.enterSort_key(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSort_key"):
                listener.exitSort_key(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSort_key"):
                return visitor.visitSort_key(self)
            else:
                return visitor.visitChildren(self)




    def sort_key(self):

        localctx = ADQLParser.Sort_keyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 204, self.RULE_sort_key)
        try:
            self.state = 961
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.ID, ADQLParser.DQ]:
                self.enterOuterAlt(localctx, 1)
                self.state = 959
                self.column_name()
                pass
            elif token in [ADQLParser.INT]:
                self.enterOuterAlt(localctx, 2)
                self.state = 960
                self.unsigned_decimal()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Sort_specificationContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Sort_specificationContext, self).__init__(parent, invokingState)
            self.parser = parser

        def sort_key(self):
            return self.getTypedRuleContext(ADQLParser.Sort_keyContext,0)


        def ordering_specification(self):
            return self.getTypedRuleContext(ADQLParser.Ordering_specificationContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_sort_specification

        def enterRule(self, listener):
            if hasattr(listener, "enterSort_specification"):
                listener.enterSort_specification(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSort_specification"):
                listener.exitSort_specification(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSort_specification"):
                return visitor.visitSort_specification(self)
            else:
                return visitor.visitChildren(self)




    def sort_specification(self):

        localctx = ADQLParser.Sort_specificationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 206, self.RULE_sort_specification)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 963
            self.sort_key()
            self.state = 965
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.ASC or _la==ADQLParser.DESC:
                self.state = 964
                self.ordering_specification()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Sort_specification_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Sort_specification_listContext, self).__init__(parent, invokingState)
            self.parser = parser

        def sort_specification(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Sort_specificationContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Sort_specificationContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.COMMA)
            else:
                return self.getToken(ADQLParser.COMMA, i)

        def getRuleIndex(self):
            return ADQLParser.RULE_sort_specification_list

        def enterRule(self, listener):
            if hasattr(listener, "enterSort_specification_list"):
                listener.enterSort_specification_list(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSort_specification_list"):
                listener.exitSort_specification_list(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSort_specification_list"):
                return visitor.visitSort_specification_list(self)
            else:
                return visitor.visitChildren(self)




    def sort_specification_list(self):

        localctx = ADQLParser.Sort_specification_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 208, self.RULE_sort_specification_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 967
            self.sort_specification()
            self.state = 972
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==ADQLParser.COMMA:
                self.state = 968
                self.match(ADQLParser.COMMA)
                self.state = 969
                self.sort_specification()
                self.state = 974
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class String_geometry_functionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.String_geometry_functionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def extract_coordsys(self):
            return self.getTypedRuleContext(ADQLParser.Extract_coordsysContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_string_geometry_function

        def enterRule(self, listener):
            if hasattr(listener, "enterString_geometry_function"):
                listener.enterString_geometry_function(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitString_geometry_function"):
                listener.exitString_geometry_function(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitString_geometry_function"):
                return visitor.visitString_geometry_function(self)
            else:
                return visitor.visitChildren(self)




    def string_geometry_function(self):

        localctx = ADQLParser.String_geometry_functionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 210, self.RULE_string_geometry_function)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 975
            self.extract_coordsys()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class String_value_expressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.String_value_expressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def character_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Character_value_expressionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_string_value_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterString_value_expression"):
                listener.enterString_value_expression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitString_value_expression"):
                listener.exitString_value_expression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitString_value_expression"):
                return visitor.visitString_value_expression(self)
            else:
                return visitor.visitChildren(self)




    def string_value_expression(self):

        localctx = ADQLParser.String_value_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 212, self.RULE_string_value_expression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 977
            self.character_value_expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class String_value_functionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.String_value_functionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def string_geometry_function(self):
            return self.getTypedRuleContext(ADQLParser.String_geometry_functionContext,0)


        def user_defined_function(self):
            return self.getTypedRuleContext(ADQLParser.User_defined_functionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_string_value_function

        def enterRule(self, listener):
            if hasattr(listener, "enterString_value_function"):
                listener.enterString_value_function(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitString_value_function"):
                listener.exitString_value_function(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitString_value_function"):
                return visitor.visitString_value_function(self)
            else:
                return visitor.visitChildren(self)




    def string_value_function(self):

        localctx = ADQLParser.String_value_functionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 214, self.RULE_string_value_function)
        try:
            self.state = 981
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.COORDSYS]:
                self.enterOuterAlt(localctx, 1)
                self.state = 979
                self.string_geometry_function()
                pass
            elif token in [ADQLParser.ID]:
                self.enterOuterAlt(localctx, 2)
                self.state = 980
                self.user_defined_function()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class SubqueryContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.SubqueryContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def query_expression(self):
            return self.getTypedRuleContext(ADQLParser.Query_expressionContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_subquery

        def enterRule(self, listener):
            if hasattr(listener, "enterSubquery"):
                listener.enterSubquery(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitSubquery"):
                listener.exitSubquery(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitSubquery"):
                return visitor.visitSubquery(self)
            else:
                return visitor.visitChildren(self)




    def subquery(self):

        localctx = ADQLParser.SubqueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 216, self.RULE_subquery)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 983
            self.match(ADQLParser.LPAREN)
            self.state = 984
            self.query_expression(0)
            self.state = 985
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Table_expressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Table_expressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def from_clause(self):
            return self.getTypedRuleContext(ADQLParser.From_clauseContext,0)


        def where_clause(self):
            return self.getTypedRuleContext(ADQLParser.Where_clauseContext,0)


        def group_by_clause(self):
            return self.getTypedRuleContext(ADQLParser.Group_by_clauseContext,0)


        def having_clause(self):
            return self.getTypedRuleContext(ADQLParser.Having_clauseContext,0)


        def order_by_clause(self):
            return self.getTypedRuleContext(ADQLParser.Order_by_clauseContext,0)


        def offset_clause(self):
            return self.getTypedRuleContext(ADQLParser.Offset_clauseContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_table_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_expression"):
                listener.enterTable_expression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_expression"):
                listener.exitTable_expression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitTable_expression"):
                return visitor.visitTable_expression(self)
            else:
                return visitor.visitChildren(self)




    def table_expression(self):

        localctx = ADQLParser.Table_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 218, self.RULE_table_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 987
            self.from_clause()
            self.state = 989
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.WHERE:
                self.state = 988
                self.where_clause()


            self.state = 992
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.GROUP:
                self.state = 991
                self.group_by_clause()


            self.state = 995
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.HAVING:
                self.state = 994
                self.having_clause()


            self.state = 998
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.ORDER:
                self.state = 997
                self.order_by_clause()


            self.state = 1001
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.OFFSET:
                self.state = 1000
                self.offset_clause()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Table_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Table_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(ADQLParser.IdentifierContext,0)


        def schema_name(self):
            return self.getTypedRuleContext(ADQLParser.Schema_nameContext,0)


        def DOT(self):
            return self.getToken(ADQLParser.DOT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_table_name

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_name"):
                listener.enterTable_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_name"):
                listener.exitTable_name(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitTable_name"):
                return visitor.visitTable_name(self)
            else:
                return visitor.visitChildren(self)




    def table_name(self):

        localctx = ADQLParser.Table_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 220, self.RULE_table_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1006
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,86,self._ctx)
            if la_ == 1:
                self.state = 1003
                self.schema_name()
                self.state = 1004
                self.match(ADQLParser.DOT)


            self.state = 1008
            self.identifier()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Table_referenceContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Table_referenceContext, self).__init__(parent, invokingState)
            self.parser = parser

        def table_name(self):
            return self.getTypedRuleContext(ADQLParser.Table_nameContext,0)


        def correlation_specification(self):
            return self.getTypedRuleContext(ADQLParser.Correlation_specificationContext,0)


        def derived_table(self):
            return self.getTypedRuleContext(ADQLParser.Derived_tableContext,0)


        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def joined_table(self):
            return self.getTypedRuleContext(ADQLParser.Joined_tableContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def table_reference(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Table_referenceContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Table_referenceContext,i)


        def JOIN(self):
            return self.getToken(ADQLParser.JOIN, 0)

        def NATURAL(self):
            return self.getToken(ADQLParser.NATURAL, 0)

        def join_type(self):
            return self.getTypedRuleContext(ADQLParser.Join_typeContext,0)


        def join_specification(self):
            return self.getTypedRuleContext(ADQLParser.Join_specificationContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_table_reference

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_reference"):
                listener.enterTable_reference(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_reference"):
                listener.exitTable_reference(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitTable_reference"):
                return visitor.visitTable_reference(self)
            else:
                return visitor.visitChildren(self)



    def table_reference(self, _p=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ADQLParser.Table_referenceContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 222
        self.enterRecursionRule(localctx, 222, self.RULE_table_reference, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1022
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,88,self._ctx)
            if la_ == 1:
                self.state = 1011
                self.table_name()
                self.state = 1013
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,87,self._ctx)
                if la_ == 1:
                    self.state = 1012
                    self.correlation_specification()


                pass

            elif la_ == 2:
                self.state = 1015
                self.derived_table()
                self.state = 1016
                self.correlation_specification()
                pass

            elif la_ == 3:
                self.state = 1018
                self.match(ADQLParser.LPAREN)
                self.state = 1019
                self.joined_table()
                self.state = 1020
                self.match(ADQLParser.RPAREN)
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 1038
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,92,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = ADQLParser.Table_referenceContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_table_reference)
                    self.state = 1024
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 1026
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==ADQLParser.NATURAL:
                        self.state = 1025
                        self.match(ADQLParser.NATURAL)


                    self.state = 1029
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if ((((_la - 135)) & ~0x3f) == 0 and ((1 << (_la - 135)) & ((1 << (ADQLParser.FULL - 135)) | (1 << (ADQLParser.INNER - 135)) | (1 << (ADQLParser.LEFT - 135)))) != 0) or _la==ADQLParser.RIGHT:
                        self.state = 1028
                        self.join_type()


                    self.state = 1031
                    self.match(ADQLParser.JOIN)
                    self.state = 1032
                    self.table_reference(0)
                    self.state = 1034
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,91,self._ctx)
                    if la_ == 1:
                        self.state = 1033
                        self.join_specification()

             
                self.state = 1040
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,92,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class Table_subqueryContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Table_subqueryContext, self).__init__(parent, invokingState)
            self.parser = parser

        def subquery(self):
            return self.getTypedRuleContext(ADQLParser.SubqueryContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_table_subquery

        def enterRule(self, listener):
            if hasattr(listener, "enterTable_subquery"):
                listener.enterTable_subquery(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTable_subquery"):
                listener.exitTable_subquery(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitTable_subquery"):
                return visitor.visitTable_subquery(self)
            else:
                return visitor.visitChildren(self)




    def table_subquery(self):

        localctx = ADQLParser.Table_subqueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 224, self.RULE_table_subquery)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1041
            self.subquery()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class TermContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.TermContext, self).__init__(parent, invokingState)
            self.parser = parser

        def factor(self):
            return self.getTypedRuleContext(ADQLParser.FactorContext,0)


        def term(self):
            return self.getTypedRuleContext(ADQLParser.TermContext,0)


        def ASTERISK(self):
            return self.getToken(ADQLParser.ASTERISK, 0)

        def SOLIDUS(self):
            return self.getToken(ADQLParser.SOLIDUS, 0)

        def MOD_SYM(self):
            return self.getToken(ADQLParser.MOD_SYM, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_term

        def enterRule(self, listener):
            if hasattr(listener, "enterTerm"):
                listener.enterTerm(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTerm"):
                listener.exitTerm(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitTerm"):
                return visitor.visitTerm(self)
            else:
                return visitor.visitChildren(self)



    def term(self, _p=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ADQLParser.TermContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 226
        self.enterRecursionRule(localctx, 226, self.RULE_term, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1044
            self.factor()
            self._ctx.stop = self._input.LT(-1)
            self.state = 1057
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,94,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 1055
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,93,self._ctx)
                    if la_ == 1:
                        localctx = ADQLParser.TermContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_term)
                        self.state = 1046
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 1047
                        self.match(ADQLParser.ASTERISK)
                        self.state = 1048
                        self.factor()
                        pass

                    elif la_ == 2:
                        localctx = ADQLParser.TermContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_term)
                        self.state = 1049
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 1050
                        self.match(ADQLParser.SOLIDUS)
                        self.state = 1051
                        self.factor()
                        pass

                    elif la_ == 3:
                        localctx = ADQLParser.TermContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_term)
                        self.state = 1052
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 1053
                        self.match(ADQLParser.MOD_SYM)
                        self.state = 1054
                        self.factor()
                        pass

             
                self.state = 1059
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,94,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class Trig_functionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Trig_functionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ACOS(self):
            return self.getToken(ADQLParser.ACOS, 0)

        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def numeric_value_expression(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Numeric_value_expressionContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Numeric_value_expressionContext,i)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def ASIN(self):
            return self.getToken(ADQLParser.ASIN, 0)

        def ATAN(self):
            return self.getToken(ADQLParser.ATAN, 0)

        def ATAN2(self):
            return self.getToken(ADQLParser.ATAN2, 0)

        def COMMA(self):
            return self.getToken(ADQLParser.COMMA, 0)

        def COS(self):
            return self.getToken(ADQLParser.COS, 0)

        def COT(self):
            return self.getToken(ADQLParser.COT, 0)

        def SIN(self):
            return self.getToken(ADQLParser.SIN, 0)

        def TAN(self):
            return self.getToken(ADQLParser.TAN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_trig_function

        def enterRule(self, listener):
            if hasattr(listener, "enterTrig_function"):
                listener.enterTrig_function(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitTrig_function"):
                listener.exitTrig_function(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitTrig_function"):
                return visitor.visitTrig_function(self)
            else:
                return visitor.visitChildren(self)




    def trig_function(self):

        localctx = ADQLParser.Trig_functionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 228, self.RULE_trig_function)
        try:
            self.state = 1107
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,95,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1060
                self.match(ADQLParser.ACOS)
                self.state = 1061
                self.match(ADQLParser.LPAREN)
                self.state = 1062
                self.numeric_value_expression(0)
                self.state = 1063
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1065
                self.match(ADQLParser.ACOS)
                self.state = 1066
                self.match(ADQLParser.LPAREN)
                self.state = 1067
                self.numeric_value_expression(0)
                self.state = 1068
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 1070
                self.match(ADQLParser.ASIN)
                self.state = 1071
                self.match(ADQLParser.LPAREN)
                self.state = 1072
                self.numeric_value_expression(0)
                self.state = 1073
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 1075
                self.match(ADQLParser.ATAN)
                self.state = 1076
                self.match(ADQLParser.LPAREN)
                self.state = 1077
                self.numeric_value_expression(0)
                self.state = 1078
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 1080
                self.match(ADQLParser.ATAN2)
                self.state = 1081
                self.match(ADQLParser.LPAREN)
                self.state = 1082
                self.numeric_value_expression(0)
                self.state = 1083
                self.match(ADQLParser.COMMA)
                self.state = 1084
                self.numeric_value_expression(0)
                self.state = 1085
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 1087
                self.match(ADQLParser.COS)
                self.state = 1088
                self.match(ADQLParser.LPAREN)
                self.state = 1089
                self.numeric_value_expression(0)
                self.state = 1090
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 1092
                self.match(ADQLParser.COT)
                self.state = 1093
                self.match(ADQLParser.LPAREN)
                self.state = 1094
                self.numeric_value_expression(0)
                self.state = 1095
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 1097
                self.match(ADQLParser.SIN)
                self.state = 1098
                self.match(ADQLParser.LPAREN)
                self.state = 1099
                self.numeric_value_expression(0)
                self.state = 1100
                self.match(ADQLParser.RPAREN)
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 1102
                self.match(ADQLParser.TAN)
                self.state = 1103
                self.match(ADQLParser.LPAREN)
                self.state = 1104
                self.numeric_value_expression(0)
                self.state = 1105
                self.match(ADQLParser.RPAREN)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Unqualified_schema_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Unqualified_schema_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(ADQLParser.ID, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_unqualified_schema_name

        def enterRule(self, listener):
            if hasattr(listener, "enterUnqualified_schema_name"):
                listener.enterUnqualified_schema_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitUnqualified_schema_name"):
                listener.exitUnqualified_schema_name(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitUnqualified_schema_name"):
                return visitor.visitUnqualified_schema_name(self)
            else:
                return visitor.visitChildren(self)




    def unqualified_schema_name(self):

        localctx = ADQLParser.Unqualified_schema_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 230, self.RULE_unqualified_schema_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1109
            self.match(ADQLParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Unsigned_decimalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Unsigned_decimalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(ADQLParser.INT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_unsigned_decimal

        def enterRule(self, listener):
            if hasattr(listener, "enterUnsigned_decimal"):
                listener.enterUnsigned_decimal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitUnsigned_decimal"):
                listener.exitUnsigned_decimal(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitUnsigned_decimal"):
                return visitor.visitUnsigned_decimal(self)
            else:
                return visitor.visitChildren(self)




    def unsigned_decimal(self):

        localctx = ADQLParser.Unsigned_decimalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 232, self.RULE_unsigned_decimal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1111
            self.match(ADQLParser.INT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Unsigned_hexadecimalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Unsigned_hexadecimalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def HEX_DIGIT(self):
            return self.getToken(ADQLParser.HEX_DIGIT, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_unsigned_hexadecimal

        def enterRule(self, listener):
            if hasattr(listener, "enterUnsigned_hexadecimal"):
                listener.enterUnsigned_hexadecimal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitUnsigned_hexadecimal"):
                listener.exitUnsigned_hexadecimal(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitUnsigned_hexadecimal"):
                return visitor.visitUnsigned_hexadecimal(self)
            else:
                return visitor.visitChildren(self)




    def unsigned_hexadecimal(self):

        localctx = ADQLParser.Unsigned_hexadecimalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 234, self.RULE_unsigned_hexadecimal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1113
            self.match(ADQLParser.HEX_DIGIT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Unsigned_literalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Unsigned_literalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def unsigned_numeric_literal(self):
            return self.getTypedRuleContext(ADQLParser.Unsigned_numeric_literalContext,0)


        def general_literal(self):
            return self.getTypedRuleContext(ADQLParser.General_literalContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_unsigned_literal

        def enterRule(self, listener):
            if hasattr(listener, "enterUnsigned_literal"):
                listener.enterUnsigned_literal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitUnsigned_literal"):
                listener.exitUnsigned_literal(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitUnsigned_literal"):
                return visitor.visitUnsigned_literal(self)
            else:
                return visitor.visitChildren(self)




    def unsigned_literal(self):

        localctx = ADQLParser.Unsigned_literalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 236, self.RULE_unsigned_literal)
        try:
            self.state = 1117
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.INT, ADQLParser.REAL, ADQLParser.HEX_DIGIT, ADQLParser.DOT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 1115
                self.unsigned_numeric_literal()
                pass
            elif token in [ADQLParser.SQ]:
                self.enterOuterAlt(localctx, 2)
                self.state = 1116
                self.general_literal()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Unsigned_numeric_literalContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Unsigned_numeric_literalContext, self).__init__(parent, invokingState)
            self.parser = parser

        def exact_numeric_literal(self):
            return self.getTypedRuleContext(ADQLParser.Exact_numeric_literalContext,0)


        def approximate_numeric_literal(self):
            return self.getTypedRuleContext(ADQLParser.Approximate_numeric_literalContext,0)


        def unsigned_hexadecimal(self):
            return self.getTypedRuleContext(ADQLParser.Unsigned_hexadecimalContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_unsigned_numeric_literal

        def enterRule(self, listener):
            if hasattr(listener, "enterUnsigned_numeric_literal"):
                listener.enterUnsigned_numeric_literal(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitUnsigned_numeric_literal"):
                listener.exitUnsigned_numeric_literal(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitUnsigned_numeric_literal"):
                return visitor.visitUnsigned_numeric_literal(self)
            else:
                return visitor.visitChildren(self)




    def unsigned_numeric_literal(self):

        localctx = ADQLParser.Unsigned_numeric_literalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 238, self.RULE_unsigned_numeric_literal)
        try:
            self.state = 1122
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.INT, ADQLParser.DOT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 1119
                self.exact_numeric_literal()
                pass
            elif token in [ADQLParser.REAL]:
                self.enterOuterAlt(localctx, 2)
                self.state = 1120
                self.approximate_numeric_literal()
                pass
            elif token in [ADQLParser.HEX_DIGIT]:
                self.enterOuterAlt(localctx, 3)
                self.state = 1121
                self.unsigned_hexadecimal()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Unsigned_value_specificationContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Unsigned_value_specificationContext, self).__init__(parent, invokingState)
            self.parser = parser

        def unsigned_literal(self):
            return self.getTypedRuleContext(ADQLParser.Unsigned_literalContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_unsigned_value_specification

        def enterRule(self, listener):
            if hasattr(listener, "enterUnsigned_value_specification"):
                listener.enterUnsigned_value_specification(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitUnsigned_value_specification"):
                listener.exitUnsigned_value_specification(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitUnsigned_value_specification"):
                return visitor.visitUnsigned_value_specification(self)
            else:
                return visitor.visitChildren(self)




    def unsigned_value_specification(self):

        localctx = ADQLParser.Unsigned_value_specificationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 240, self.RULE_unsigned_value_specification)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1124
            self.unsigned_literal()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class User_defined_functionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.User_defined_functionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def user_defined_function_name(self):
            return self.getTypedRuleContext(ADQLParser.User_defined_function_nameContext,0)


        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def user_defined_function_param(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.User_defined_function_paramContext)
            else:
                return self.getTypedRuleContext(ADQLParser.User_defined_function_paramContext,i)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.COMMA)
            else:
                return self.getToken(ADQLParser.COMMA, i)

        def getRuleIndex(self):
            return ADQLParser.RULE_user_defined_function

        def enterRule(self, listener):
            if hasattr(listener, "enterUser_defined_function"):
                listener.enterUser_defined_function(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitUser_defined_function"):
                listener.exitUser_defined_function(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitUser_defined_function"):
                return visitor.visitUser_defined_function(self)
            else:
                return visitor.visitChildren(self)




    def user_defined_function(self):

        localctx = ADQLParser.User_defined_functionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 242, self.RULE_user_defined_function)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1126
            self.user_defined_function_name()
            self.state = 1127
            self.match(ADQLParser.LPAREN)
            self.state = 1136
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ADQLParser.ABS) | (1 << ADQLParser.ACOS) | (1 << ADQLParser.AREA) | (1 << ADQLParser.ASIN) | (1 << ADQLParser.ATAN) | (1 << ADQLParser.ATAN2) | (1 << ADQLParser.BOX) | (1 << ADQLParser.CEILING) | (1 << ADQLParser.CENTROID) | (1 << ADQLParser.CIRCLE) | (1 << ADQLParser.CONTAINS) | (1 << ADQLParser.COORD1) | (1 << ADQLParser.COORD2) | (1 << ADQLParser.COORDSYS) | (1 << ADQLParser.COS) | (1 << ADQLParser.COT) | (1 << ADQLParser.DEGREES) | (1 << ADQLParser.DISTANCE) | (1 << ADQLParser.EXP) | (1 << ADQLParser.FLOOR) | (1 << ADQLParser.INTERSECTS) | (1 << ADQLParser.LOG) | (1 << ADQLParser.LOG10) | (1 << ADQLParser.MOD) | (1 << ADQLParser.PI) | (1 << ADQLParser.POINT) | (1 << ADQLParser.POLYGON) | (1 << ADQLParser.POWER) | (1 << ADQLParser.RADIANS) | (1 << ADQLParser.REGION) | (1 << ADQLParser.SIN) | (1 << ADQLParser.SQRT) | (1 << ADQLParser.TAN) | (1 << ADQLParser.TRUNCATE) | (1 << ADQLParser.AVG))) != 0) or _la==ADQLParser.COUNT or _la==ADQLParser.FALSE or _la==ADQLParser.MAX or _la==ADQLParser.MIN or ((((_la - 235)) & ~0x3f) == 0 and ((1 << (_la - 235)) & ((1 << (ADQLParser.SUM - 235)) | (1 << (ADQLParser.TRUE - 235)) | (1 << (ADQLParser.INT - 235)) | (1 << (ADQLParser.REAL - 235)) | (1 << (ADQLParser.HEX_DIGIT - 235)) | (1 << (ADQLParser.ID - 235)) | (1 << (ADQLParser.TILDE - 235)) | (1 << (ADQLParser.LPAREN - 235)) | (1 << (ADQLParser.PLUS - 235)) | (1 << (ADQLParser.MINUS - 235)) | (1 << (ADQLParser.DOT - 235)))) != 0) or _la==ADQLParser.DQ or _la==ADQLParser.SQ:
                self.state = 1128
                self.user_defined_function_param()
                self.state = 1133
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==ADQLParser.COMMA:
                    self.state = 1129
                    self.match(ADQLParser.COMMA)
                    self.state = 1130
                    self.user_defined_function_param()
                    self.state = 1135
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 1138
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class User_defined_function_nameContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.User_defined_function_nameContext, self).__init__(parent, invokingState)
            self.parser = parser

        def regular_identifier(self):
            return self.getTypedRuleContext(ADQLParser.Regular_identifierContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_user_defined_function_name

        def enterRule(self, listener):
            if hasattr(listener, "enterUser_defined_function_name"):
                listener.enterUser_defined_function_name(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitUser_defined_function_name"):
                listener.exitUser_defined_function_name(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitUser_defined_function_name"):
                return visitor.visitUser_defined_function_name(self)
            else:
                return visitor.visitChildren(self)




    def user_defined_function_name(self):

        localctx = ADQLParser.User_defined_function_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 244, self.RULE_user_defined_function_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1140
            self.regular_identifier()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class User_defined_function_paramContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.User_defined_function_paramContext, self).__init__(parent, invokingState)
            self.parser = parser

        def value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Value_expressionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_user_defined_function_param

        def enterRule(self, listener):
            if hasattr(listener, "enterUser_defined_function_param"):
                listener.enterUser_defined_function_param(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitUser_defined_function_param"):
                listener.exitUser_defined_function_param(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitUser_defined_function_param"):
                return visitor.visitUser_defined_function_param(self)
            else:
                return visitor.visitChildren(self)




    def user_defined_function_param(self):

        localctx = ADQLParser.User_defined_function_paramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 246, self.RULE_user_defined_function_param)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1142
            self.value_expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Value_expressionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Value_expressionContext, self).__init__(parent, invokingState)
            self.parser = parser

        def numeric_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Numeric_value_expressionContext,0)


        def string_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.String_value_expressionContext,0)


        def boolean_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Boolean_value_expressionContext,0)


        def geometry_value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Geometry_value_expressionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_value_expression

        def enterRule(self, listener):
            if hasattr(listener, "enterValue_expression"):
                listener.enterValue_expression(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitValue_expression"):
                listener.exitValue_expression(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitValue_expression"):
                return visitor.visitValue_expression(self)
            else:
                return visitor.visitChildren(self)




    def value_expression(self):

        localctx = ADQLParser.Value_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 248, self.RULE_value_expression)
        try:
            self.state = 1148
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,100,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1144
                self.numeric_value_expression(0)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1145
                self.string_value_expression()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 1146
                self.boolean_value_expression()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 1147
                self.geometry_value_expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Value_expression_primaryContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Value_expression_primaryContext, self).__init__(parent, invokingState)
            self.parser = parser

        def unsigned_value_specification(self):
            return self.getTypedRuleContext(ADQLParser.Unsigned_value_specificationContext,0)


        def column_reference(self):
            return self.getTypedRuleContext(ADQLParser.Column_referenceContext,0)


        def set_function_specification(self):
            return self.getTypedRuleContext(ADQLParser.Set_function_specificationContext,0)


        def LPAREN(self):
            return self.getToken(ADQLParser.LPAREN, 0)

        def value_expression(self):
            return self.getTypedRuleContext(ADQLParser.Value_expressionContext,0)


        def RPAREN(self):
            return self.getToken(ADQLParser.RPAREN, 0)

        def getRuleIndex(self):
            return ADQLParser.RULE_value_expression_primary

        def enterRule(self, listener):
            if hasattr(listener, "enterValue_expression_primary"):
                listener.enterValue_expression_primary(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitValue_expression_primary"):
                listener.exitValue_expression_primary(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitValue_expression_primary"):
                return visitor.visitValue_expression_primary(self)
            else:
                return visitor.visitChildren(self)




    def value_expression_primary(self):

        localctx = ADQLParser.Value_expression_primaryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 250, self.RULE_value_expression_primary)
        try:
            self.state = 1157
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ADQLParser.INT, ADQLParser.REAL, ADQLParser.HEX_DIGIT, ADQLParser.DOT, ADQLParser.SQ]:
                self.enterOuterAlt(localctx, 1)
                self.state = 1150
                self.unsigned_value_specification()
                pass
            elif token in [ADQLParser.ID, ADQLParser.DQ]:
                self.enterOuterAlt(localctx, 2)
                self.state = 1151
                self.column_reference()
                pass
            elif token in [ADQLParser.AVG, ADQLParser.COUNT, ADQLParser.MAX, ADQLParser.MIN, ADQLParser.SUM]:
                self.enterOuterAlt(localctx, 3)
                self.state = 1152
                self.set_function_specification()
                pass
            elif token in [ADQLParser.LPAREN]:
                self.enterOuterAlt(localctx, 4)
                self.state = 1153
                self.match(ADQLParser.LPAREN)
                self.state = 1154
                self.value_expression()
                self.state = 1155
                self.match(ADQLParser.RPAREN)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Where_clauseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.Where_clauseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def WHERE(self):
            return self.getToken(ADQLParser.WHERE, 0)

        def search_condition(self):
            return self.getTypedRuleContext(ADQLParser.Search_conditionContext,0)


        def getRuleIndex(self):
            return ADQLParser.RULE_where_clause

        def enterRule(self, listener):
            if hasattr(listener, "enterWhere_clause"):
                listener.enterWhere_clause(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitWhere_clause"):
                listener.exitWhere_clause(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitWhere_clause"):
                return visitor.visitWhere_clause(self)
            else:
                return visitor.visitChildren(self)




    def where_clause(self):

        localctx = ADQLParser.Where_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 252, self.RULE_where_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1159
            self.match(ADQLParser.WHERE)
            self.state = 1160
            self.search_condition(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class With_queryContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(ADQLParser.With_queryContext, self).__init__(parent, invokingState)
            self.parser = parser

        def query_name(self):
            return self.getTypedRuleContext(ADQLParser.Query_nameContext,0)


        def AS(self):
            return self.getToken(ADQLParser.AS, 0)

        def LPAREN(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.LPAREN)
            else:
                return self.getToken(ADQLParser.LPAREN, i)

        def RPAREN(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.RPAREN)
            else:
                return self.getToken(ADQLParser.RPAREN, i)

        def column_name(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(ADQLParser.Column_nameContext)
            else:
                return self.getTypedRuleContext(ADQLParser.Column_nameContext,i)


        def query_specification(self):
            return self.getTypedRuleContext(ADQLParser.Query_specificationContext,0)


        def COMMA(self, i=None):
            if i is None:
                return self.getTokens(ADQLParser.COMMA)
            else:
                return self.getToken(ADQLParser.COMMA, i)

        def getRuleIndex(self):
            return ADQLParser.RULE_with_query

        def enterRule(self, listener):
            if hasattr(listener, "enterWith_query"):
                listener.enterWith_query(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitWith_query"):
                listener.exitWith_query(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitWith_query"):
                return visitor.visitWith_query(self)
            else:
                return visitor.visitChildren(self)




    def with_query(self):

        localctx = ADQLParser.With_queryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 254, self.RULE_with_query)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1162
            self.query_name()
            self.state = 1174
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.LPAREN:
                self.state = 1163
                self.match(ADQLParser.LPAREN)
                self.state = 1164
                self.column_name()
                self.state = 1169
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==ADQLParser.COMMA:
                    self.state = 1165
                    self.match(ADQLParser.COMMA)
                    self.state = 1166
                    self.column_name()
                    self.state = 1171
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 1172
                self.match(ADQLParser.RPAREN)


            self.state = 1176
            self.match(ADQLParser.AS)
            self.state = 1177
            self.match(ADQLParser.LPAREN)
            self.state = 1179
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ADQLParser.SELECT or _la==ADQLParser.WITH:
                self.state = 1178
                self.query_specification()


            self.state = 1181
            self.match(ADQLParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx, ruleIndex, predIndex):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[11] = self.boolean_term_sempred
        self._predicates[17] = self.character_value_expression_sempred
        self._predicates[72] = self.numeric_value_expression_sempred
        self._predicates[84] = self.query_expression_sempred
        self._predicates[87] = self.query_term_sempred
        self._predicates[92] = self.search_condition_sempred
        self._predicates[111] = self.table_reference_sempred
        self._predicates[113] = self.term_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def boolean_term_sempred(self, localctx, predIndex):
            if predIndex == 0:
                return self.precpred(self._ctx, 1)
         

    def character_value_expression_sempred(self, localctx, predIndex):
            if predIndex == 1:
                return self.precpred(self._ctx, 3)
         

    def numeric_value_expression_sempred(self, localctx, predIndex):
            if predIndex == 2:
                return self.precpred(self._ctx, 5)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 4)
         

            if predIndex == 4:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 5:
                return self.precpred(self._ctx, 2)
         

            if predIndex == 6:
                return self.precpred(self._ctx, 1)
         

    def query_expression_sempred(self, localctx, predIndex):
            if predIndex == 7:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 8:
                return self.precpred(self._ctx, 2)
         

    def query_term_sempred(self, localctx, predIndex):
            if predIndex == 9:
                return self.precpred(self._ctx, 2)
         

    def search_condition_sempred(self, localctx, predIndex):
            if predIndex == 10:
                return self.precpred(self._ctx, 1)
         

    def table_reference_sempred(self, localctx, predIndex):
            if predIndex == 11:
                return self.precpred(self._ctx, 2)
         

    def term_sempred(self, localctx, predIndex):
            if predIndex == 12:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 13:
                return self.precpred(self._ctx, 2)
         

            if predIndex == 14:
                return self.precpred(self._ctx, 1)
         




