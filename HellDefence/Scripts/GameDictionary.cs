using UnityEngine;
using System.Collections.Generic;

public class GameDictionary : MonoBehaviour {

    private static Dictionary<SpellName, KeyCode> _spellKeyCodes;
    private static Dictionary<SpellName, Sprite> _spellIcons;
    private static Dictionary<SpellName, GameObject> _spellGameObjects;
    private static Dictionary<SpellName, SpellType> _spellTypes;
    private static Dictionary<SpellName, float> _spellCastingTimes;
    private static Dictionary<SpellName, float> _spellCooldownTimes;
    private static Dictionary<SpellName, string> _spellDescriptions;
    private static Dictionary<SpellName, float> _spellDefaultCastDistance;
    private static Dictionary<SpellName, float> _spellMinCastDistance;
    private static Dictionary<SpellName, float> _spellMaxCastDistance;

    private static Dictionary<StatCategory, Sprite> _statIcons;

    void Awake()
    {
        InitializeSpellKeyCodes();
        InitializeSpellIcons();
        InitializeSpellObjects();
        InitializeSpellTypes();
        InitializeSpellCastingTimes();
        InitializeSpellCooldowns();
        InitializeSpellCastDistances();

        InitializeStatIcons();
    }

    public static List<SpellName> GetAllSpells()
    {
        return new List<SpellName>(_spellKeyCodes.Keys);
    }

    // Spell Key Codes
    private void InitializeSpellKeyCodes()
    {
        _spellKeyCodes = new Dictionary<SpellName, KeyCode>();

        _spellKeyCodes.Add(SpellName.Fireball, KeyCode.G);
        _spellKeyCodes.Add(SpellName.Scourge, KeyCode.F);
        _spellKeyCodes.Add(SpellName.Teleport, KeyCode.R);
        _spellKeyCodes.Add(SpellName.Gravity, KeyCode.Y);
        _spellKeyCodes.Add(SpellName.PlasmaField, KeyCode.C);
        _spellKeyCodes.Add(SpellName.Domestication, KeyCode.B);
        _spellKeyCodes.Add(SpellName.BulletStorm, KeyCode.T);
        _spellKeyCodes.Add(SpellName.GroundShock, KeyCode.Z);
        _spellKeyCodes.Add(SpellName.LavaBeam, KeyCode.X);
        // ...
    }

    public static KeyCode GetSpellKeyCode(SpellName spellName)
    {
        KeyCode spellKeyCode;
        if(_spellKeyCodes.TryGetValue(spellName, out spellKeyCode))
        {
            return spellKeyCode;
        }

        return KeyCode.None;
    }

    // Spell Icons
    private void InitializeSpellIcons()
    {
        _spellIcons = new Dictionary<SpellName, Sprite>();

        _spellIcons.Add(SpellName.Fireball, Resources.Load("Fireball", typeof(Sprite)) as Sprite);
        _spellIcons.Add(SpellName.Scourge, Resources.Load("Scourge", typeof(Sprite)) as Sprite);
        _spellIcons.Add(SpellName.Teleport, Resources.Load("Teleport", typeof(Sprite)) as Sprite);
        _spellIcons.Add(SpellName.Gravity, Resources.Load("Gravity", typeof(Sprite)) as Sprite);
        _spellIcons.Add(SpellName.PlasmaField, Resources.Load("Plasmafield", typeof(Sprite)) as Sprite);
        _spellIcons.Add(SpellName.Domestication, Resources.Load("Domestication", typeof(Sprite)) as Sprite);
        _spellIcons.Add(SpellName.BulletStorm, Resources.Load("Bulletstorm", typeof(Sprite)) as Sprite);
        _spellIcons.Add(SpellName.GroundShock, Resources.Load("GroundShock", typeof(Sprite)) as Sprite);
        _spellIcons.Add(SpellName.LavaBeam, Resources.Load("LavaBeam", typeof(Sprite)) as Sprite);
        // ...
    }

    public static Sprite GetSpellIcon(SpellName spellName)
    {
        Sprite spellIcon;
        if (_spellIcons.TryGetValue(spellName, out spellIcon))
        {
            return spellIcon;
        }

        return null;
    }

    // Spell Prefabs
    private void InitializeSpellObjects()
    {
        _spellGameObjects = new Dictionary<SpellName, GameObject>();

        _spellGameObjects.Add(SpellName.Fireball, Resources.Load("fireball", typeof(GameObject)) as GameObject);
        _spellGameObjects.Add(SpellName.Scourge, Resources.Load("scourge", typeof(GameObject)) as GameObject);
        _spellGameObjects.Add(SpellName.Teleport, Resources.Load("teleport", typeof(GameObject)) as GameObject);
        _spellGameObjects.Add(SpellName.Gravity, Resources.Load("gravity", typeof(GameObject)) as GameObject);
        _spellGameObjects.Add(SpellName.PlasmaField, Resources.Load("PlasmaField", typeof(GameObject)) as GameObject);
        _spellGameObjects.Add(SpellName.Domestication, Resources.Load("Domestication", typeof(GameObject)) as GameObject);
        _spellGameObjects.Add(SpellName.BulletStorm, Resources.Load("BulletStorm", typeof(GameObject)) as GameObject);
        _spellGameObjects.Add(SpellName.GroundShock, Resources.Load("GroundShock", typeof(GameObject)) as GameObject);
        _spellGameObjects.Add(SpellName.LavaBeam, Resources.Load("LavaBeam", typeof(GameObject)) as GameObject);
        // ...
    }

    public static GameObject GetSpellGameObject(SpellName spellName)
    {
        GameObject spellGameObject;
        if(_spellGameObjects.TryGetValue(spellName, out spellGameObject) )
        {
            return spellGameObject;
        }
        
        return null;
    }

    // Spell Type
    private void InitializeSpellTypes()
    {
        _spellTypes = new Dictionary<SpellName, SpellType>();

        _spellTypes.Add(SpellName.Fireball, SpellType.NormalCast);
        _spellTypes.Add(SpellName.Scourge, SpellType.InstantCast);
        _spellTypes.Add(SpellName.Teleport, SpellType.NormalCast);
        _spellTypes.Add(SpellName.Gravity, SpellType.NormalCast);
        _spellTypes.Add(SpellName.PlasmaField, SpellType.InstantCast);
        _spellTypes.Add(SpellName.Domestication, SpellType.InstantCast);
        _spellTypes.Add(SpellName.BulletStorm, SpellType.NormalCast);
        _spellTypes.Add(SpellName.GroundShock, SpellType.InstantCast);
        _spellTypes.Add(SpellName.LavaBeam, SpellType.NormalCast);
        // ...
    }

    public static SpellType GetSpellType(SpellName spellName)
    {
        SpellType spellType;
        if(_spellTypes.TryGetValue(spellName, out spellType))
        {
            return spellType;
        }

        return SpellType.None;
    }

    // Spell Casting Time
    private void InitializeSpellCastingTimes()
    {
        _spellCastingTimes = new Dictionary<SpellName, float>();

        _spellCastingTimes.Add(SpellName.Fireball, .2f);
        _spellCastingTimes.Add(SpellName.Scourge, 1f);
        _spellCastingTimes.Add(SpellName.Teleport, .05f);
        _spellCastingTimes.Add(SpellName.Gravity, .2f);
        _spellCastingTimes.Add(SpellName.PlasmaField, .0f);
        _spellCastingTimes.Add(SpellName.Domestication, .1f);
        _spellCastingTimes.Add(SpellName.BulletStorm, .3f);
        _spellCastingTimes.Add(SpellName.GroundShock, .1f);
        _spellCastingTimes.Add(SpellName.LavaBeam, .3f);
    }

    public static float GetSpellCastingTime(SpellName spellName)
    {
        float spellCastingTime;
        if (_spellCastingTimes.TryGetValue(spellName, out spellCastingTime))
        {
            return spellCastingTime;
        }

        return -1;
    }

    // Spell Cooldown Time
    private void InitializeSpellCooldowns()
    {
        _spellCooldownTimes = new Dictionary<SpellName, float>();

        _spellCooldownTimes.Add(SpellName.Fireball, 3f);
        _spellCooldownTimes.Add(SpellName.Scourge, 4f);
        _spellCooldownTimes.Add(SpellName.Teleport, 8f);
        _spellCooldownTimes.Add(SpellName.Gravity, 15f);
        _spellCooldownTimes.Add(SpellName.PlasmaField, 20f);
        _spellCooldownTimes.Add(SpellName.Domestication, 120f);
        _spellCooldownTimes.Add(SpellName.BulletStorm, 20f);
        _spellCooldownTimes.Add(SpellName.GroundShock, 30f);
        _spellCooldownTimes.Add(SpellName.LavaBeam, 25f);
    }

    public static float GetSpellCooldownTime(SpellName spellName)
    {
        float spellCooldownTime;
        if (_spellCooldownTimes.TryGetValue(spellName, out spellCooldownTime))
        {
            return spellCooldownTime;
        }

        return -1;
    }

    //Spell cast distances
    private void InitializeSpellCastDistances()
    {
        _spellDefaultCastDistance = new Dictionary<SpellName, float>();
        _spellMinCastDistance = new Dictionary<SpellName, float>();
        _spellMaxCastDistance = new Dictionary<SpellName, float>();

        _spellDefaultCastDistance.Add(SpellName.Fireball, 10f);
        _spellMinCastDistance.Add(SpellName.Fireball, 5f);
        _spellMaxCastDistance.Add(SpellName.Fireball, 30f);

        _spellDefaultCastDistance.Add(SpellName.Teleport, 20f);
        _spellMinCastDistance.Add(SpellName.Teleport, 3f);
        _spellMaxCastDistance.Add(SpellName.Teleport, 30f);

        _spellDefaultCastDistance.Add(SpellName.BulletStorm, 10f);
        _spellMinCastDistance.Add(SpellName.BulletStorm, .5f);
        _spellMaxCastDistance.Add(SpellName.BulletStorm, 35f);

        _spellDefaultCastDistance.Add(SpellName.Gravity, 10f);
        _spellMinCastDistance.Add(SpellName.Gravity, 5f);
        _spellMaxCastDistance.Add(SpellName.Gravity, 30f);

        _spellDefaultCastDistance.Add(SpellName.LavaBeam, 10f);
        _spellMinCastDistance.Add(SpellName.LavaBeam, 5f);
        _spellMaxCastDistance.Add(SpellName.LavaBeam, 30f);
    }

    public static float GetDefaultSpellCastDistance(SpellName spellName)
    {
        float defaultDistance;
        if (_spellDefaultCastDistance.TryGetValue(spellName, out defaultDistance))
        {
            return defaultDistance;
        }

        return -1;
    }

    public static float GetMinSpellCastDistance(SpellName spellName)
    {
        float minDistance;
        if (_spellMinCastDistance.TryGetValue(spellName, out minDistance))
        {
            return minDistance;
        }

        return -1;
    }

    public static float GetMaxSpellCastDistance(SpellName spellName)
    {
        float maxDistance;
        if (_spellMaxCastDistance.TryGetValue(spellName, out maxDistance))
        {
            return maxDistance;
        }

        return -1;
    }

    // Stat Icons
    private void InitializeStatIcons()
    {
        _statIcons = new Dictionary<StatCategory, Sprite>();

        _statIcons.Add(StatCategory.Cooldown, Resources.Load("Cooldown", typeof(Sprite)) as Sprite);
        _statIcons.Add(StatCategory.Damage, Resources.Load("Damage", typeof(Sprite)) as Sprite);
        _statIcons.Add(StatCategory.MaxHealth, Resources.Load("MaxHealth", typeof(Sprite)) as Sprite);
        _statIcons.Add(StatCategory.Regeneration, Resources.Load("Regeneration", typeof(Sprite)) as Sprite);
        _statIcons.Add(StatCategory.Speed, Resources.Load("Speed", typeof(Sprite)) as Sprite);

        // ...
    }

    public static Sprite GetStatIcon(StatCategory statCategory)
    {
        Sprite statIcon;
        if (_statIcons.TryGetValue(statCategory, out statIcon))
        {
            return statIcon;
        }

        return null;
    }


    // Enemies Infos
    public static bool AreEnemies(string tag1, string tag2)
    {
        if(tag1 == "Player" && tag2 == "Mob" ||
           tag1 == "PlayerPet" && tag2 == "Mob" ||
           tag1 == "Mob" && tag2 == "Player" ||
           tag1 == "Mob" && tag2 == "PlayerPet")
        {
            return true;
        }

        return false;
    }
}
