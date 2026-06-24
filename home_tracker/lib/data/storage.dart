import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';
import '../models/models.dart';

class Storage {
  static const _keyCategories = 'ht_categories';
  static const _keyChores = 'ht_chores';
  static const _keyPurchases = 'ht_purchases';
  static const _keyEvents = 'ht_events';

  static final _uuid = const Uuid();

  static Future<SharedPreferences> get _prefs => SharedPreferences.getInstance();

  static String genId() => _uuid.v4().substring(0, 8);

  // Categories
  static Future<List<String>> loadCategories() async {
    final prefs = await _prefs;
    final raw = prefs.getStringList(_keyCategories);
    if (raw != null && raw.isNotEmpty) return raw;
    return ['Хозяйственные дела'];
  }

  static Future<void> saveCategories(List<String> cats) async {
    final prefs = await _prefs;
    await prefs.setStringList(_keyCategories, cats);
  }

  // Chores
  static Future<List<Chore>> loadChores() async {
    final prefs = await _prefs;
    final raw = prefs.getString(_keyChores);
    if (raw == null || raw.isEmpty) return [];
    final list = jsonDecode(raw) as List;
    return list.map((e) => Chore.fromJson(e as Map<String, dynamic>)).toList();
  }

  static Future<void> saveChores(List<Chore> chores) async {
    final prefs = await _prefs;
    await prefs.setString(_keyChores, jsonEncode(chores.map((c) => c.toJson()).toList()));
  }

  // Purchases
  static Future<List<Purchase>> loadPurchases() async {
    final prefs = await _prefs;
    final raw = prefs.getString(_keyPurchases);
    if (raw == null || raw.isEmpty) return [];
    final list = jsonDecode(raw) as List;
    return list.map((e) => Purchase.fromJson(e as Map<String, dynamic>)).toList();
  }

  static Future<void> savePurchases(List<Purchase> purchases) async {
    final prefs = await _prefs;
    await prefs.setString(_keyPurchases, jsonEncode(purchases.map((p) => p.toJson()).toList()));
  }

  // Events
  static Future<List<FamilyEvent>> loadEvents() async {
    final prefs = await _prefs;
    final raw = prefs.getString(_keyEvents);
    if (raw == null || raw.isEmpty) return [];
    final list = jsonDecode(raw) as List;
    return list.map((e) => FamilyEvent.fromJson(e as Map<String, dynamic>)).toList();
  }

  static Future<void> saveEvents(List<FamilyEvent> events) async {
    final prefs = await _prefs;
    await prefs.setString(_keyEvents, jsonEncode(events.map((e) => e.toJson()).toList()));
  }
}
