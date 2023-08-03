# DKLinkBuilder.py
# by pubins.taylor
# created 10MAY22
# modified 03AUG23
# version 0.1.0
# Houses the generics for Selenium WebDriver Link Builders

from src.Globals import FGSystem, FGPosGrp, Savant, SavantPosGrp, SavantDownload


def DKFGLinkBuilder(*projections: list[FGSystem], pos: list[FGPosGrp] = (FGPosGrp.HIT, FGPosGrp.PIT)) -> list[
    dict[str, str]]:
    """
    Builds Fangraphs URLs based on user need.
    :param projections: A list of Projections enums representing the desired FanGraphs projection options
    :param pos: A list of position groups. Either hitters, pitchers, or both.  Defaults to both
    :return: A list of dictionary items.  The list represents the URL objects and the dict is keyed by the URL id which
    """

    urls = []
    for grp in pos:
        for proj in projections:
            fgURL = "https://www.fangraphs.com/projections.aspx?pos=all&stats=" + grp.value + "&type=" + \
                    proj.value + "&team=0&lg=all&players=0"
            fg = {"id": proj.value + "_" + grp.value, "url": fgURL}
            urls.append(fg)

    return urls


def DKSavantLinkBuilder(statcast: list[Savant], pos: list[SavantPosGrp] = (SavantPosGrp.HIT, SavantPosGrp.PIT)) -> list[
    dict[str: str]]:
    """
    Builds baseball.savant URLs based on user need.
    :param statcast: A list of Savant enums representing the desired baseball savant stats
    :param pos: A list of position groups. Either hitters, pitchers, or both.  Defaults to both
    :return: A list of dictionary items.  The list represents the URL objects and the dict is keyed by the URL id which
    """

    minEvents: str
    urls = []
    for grp in pos:
        if grp == SavantPosGrp.HIT:
            minEvents = "25"  # stands for qualified
        elif grp == SavantPosGrp.PIT:
            minEvents = "1"
        for stats in statcast:
            url = "https://baseballsavant.mlb.com/leaderboard/" + stats.value + "?type=" + grp.value + "&min=" \
                  + minEvents
            if stats == Savant.xStats:
                download = SavantDownload.xStats
            savant = {
                "id": stats.value + "_" + grp.value[0:3],  # subscript operator to get the first 3 letters
                "url": url,
                "download": download.value
            }
            urls.append(savant)

    return urls

