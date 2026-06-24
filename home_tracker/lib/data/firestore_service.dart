import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/models.dart';

class FirestoreService {
  static const _familyId = 'family_main';

  static final _db = FirebaseFirestore.instance;
  static CollectionReference get _family => _db.collection('families').doc(_familyId).collection('data');

  static String genId() => _db.collection('_').doc().id.substring(0, 8);

  static Future<void> init() async {
    await _db.collection('families').doc(_familyId).set({'createdAt': FieldValue.serverTimestamp()}, SetOptions(merge: true));
  }

  // --- Categories ---
  static Future<List<String>> loadCategories() async {
    final snap = await _family.doc('categories').get();
    final raw = snap.data() as Map<String, dynamic>?;
    if (raw == null || raw['items'] == null) return ['Хозяйственные дела'];
    return List<String>.from(raw['items'] as List);
  }

  static Future<void> saveCategories(List<String> cats) async {
    await _family.doc('categories').set({'items': cats});
  }

  // --- Chores ---
  static Future<List<Chore>> loadChores() async {
    final snap = await _family.doc('chores').get();
    final raw = snap.data() as Map<String, dynamic>?;
    if (raw == null || raw['items'] == null) return [];
    final list = raw['items'] as List;
    return list.map((e) => Chore.fromJson(e as Map<String, dynamic>)).toList();
  }

  static Future<void> saveChores(List<Chore> chores) async {
    await _family.doc('chores').set({'items': chores.map((c) => c.toJson()).toList()});
  }

  // --- Purchases ---
  static Future<List<Purchase>> loadPurchases() async {
    final snap = await _family.doc('purchases').get();
    final raw = snap.data() as Map<String, dynamic>?;
    if (raw == null || raw['items'] == null) return [];
    final list = raw['items'] as List;
    return list.map((e) => Purchase.fromJson(e as Map<String, dynamic>)).toList();
  }

  static Future<void> savePurchases(List<Purchase> purchases) async {
    await _family.doc('purchases').set({'items': purchases.map((p) => p.toJson()).toList()});
  }

  // --- Events ---
  static Future<List<FamilyEvent>> loadEvents() async {
    final snap = await _family.doc('events').get();
    final raw = snap.data() as Map<String, dynamic>?;
    if (raw == null || raw['items'] == null) return [];
    final list = raw['items'] as List;
    return list.map((e) => FamilyEvent.fromJson(e as Map<String, dynamic>)).toList();
  }

  static Future<void> saveEvents(List<FamilyEvent> events) async {
    await _family.doc('events').set({'items': events.map((e) => e.toJson()).toList()});
  }

  // --- Real-time subscription ---
  static Stream<void> get dataChanges {
    return _family.snapshots().map((_) => null);
  }
}
