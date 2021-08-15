
public class Stat {

    public StatCategory category { get; private set; }
    public StatType type { get; private set; }
    public float factorValue { get; private set; }

    public Stat(StatCategory statCategory, StatType statType, float factorValue)
    {
        category = statCategory;
        type = statType;
        this.factorValue = factorValue;
    }

    public Stat()
    {
        category = StatCategory.None;
        type = StatType.None;
        factorValue = 0;
    }

    public Stat(Stat stat)
    {
        category = stat.category;
        type = stat.type;
        factorValue = stat.factorValue;
    }

    public string Description()
    {
        string result = "+";
        if(type == StatType.Quota)
        {
            result += factorValue * 100 + "% " + category.ToString();
        }
        else if(type == StatType.Constant)
        {
            result += factorValue + " " + category.ToString();
        }

        return result;
    }
}
