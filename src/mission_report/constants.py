
class Coalition:
    neutral = 0
    coal_1 = 1
    coal_2 = 2

    Allies = 1
    Axis = 2
    Entente = 3
    CentralPowers = 4

    none = 5
    Red = 6
    Blue = 7
    Yellow = 8
    Green = 9


class Country:
    neutral = 0
    USSR = 101
    GreatBritain = 102
    USA = 103
    Germany = 201
    Italy = 202
    Japan = 203
    France = 301
    GreatBritainWW1 = 302
    UnitedStatesWW1 = 303
    Belgium = 304
    Russia = 305
    GermanyWW1 = 401
    AustriaHungary = 402

    Red = 901
    Blue = 902
    Yellow = 903
    Green = 904


COUNTRIES_COALITION_DEFAULT = {
    Country.neutral: Coalition.neutral,
    Country.Red: Coalition.neutral,
    Country.Blue: Coalition.neutral,
    Country.Yellow: Coalition.neutral,
    Country.Green: Coalition.neutral,

    Country.USSR: Coalition.Allies,
    Country.GreatBritain: Coalition.Allies,
    Country.USA: Coalition.Allies,

    Country.France: Coalition.Allies,
    Country.GreatBritainWW1: Coalition.Allies,
    Country.UnitedStatesWW1: Coalition.Allies,
    Country.Belgium: Coalition.Allies,
    Country.Russia: Coalition.Allies,

    Country.Germany: Coalition.Axis,
    Country.Italy: Coalition.Axis,
    Country.Japan: Coalition.Axis,

    Country.GermanyWW1: Coalition.Axis,
    Country.AustriaHungary: Coalition.Axis,
}


COALITION_ALIAS = {
    0: Coalition.neutral,
    1: Coalition.coal_1,
    2: Coalition.coal_2,
    3: Coalition.coal_1,
    4: Coalition.coal_2,
    5: Coalition.none,
    6: Coalition.neutral,
    7: Coalition.neutral,
    8: Coalition.neutral,
    9: Coalition.neutral,
}


GAME_CLASSES = (
    'CAeroplaneFragment',
    'CAerostat',
    'CAerostatAI',
    'CAerostatMonitor',
    'CAIPoi',
    'CAIPoiMonitor',
    'CAirfield',
    'CAnimationOperator',
    'CAnimationOperatorMonitor',
    'CAttachedVehicle',
    'CBallistics',
    'CBaloonWinch',
    'CBanner',
    'CBatchBallistics',
    'CBatchExplosion',
    'CBatchFactory',
    'CBatchFreeEffect',
    'CBatchRocketFireworks',
    'CBatchTrash',
    'CBatchTrashAnimated',
    'CBFManager',
    'CBlocksArray',
    'CBombSiteAim',
    'CBot',
    'CBotAimingHead',
    'CBotCharacter',
    'CBotController',
    'CBotFieldController',
    'CBotHead',
    'CBotInputController',
    'CCameraOperator',
    'CCameraOperatorMonitor',
    'CCloudSky',
    'CClusterBallistics',
    'CCommanderInputController',
    'CComplexTrigger',
    'CCumulativeRocket',
    'CDFMission',
    'CDistantLOD',
    'CDrogueChute',
    'CDummyObject',
    'CEjectionPlace',
    'CEjectorController',
    'CFlag',
    'CFlareGun',
    'CFlexRope',
    'CFokkerDr1Monitor',
    'CForestBody',
    'CGameChat',
    'CGameMission',
    'CGoProCamera',
    'CInfluenceArea',
    'CInfluenceAreaMonitor',
    'CLandObjectMonitor',
    'CLauncherRamp',
    'CMouseControlCameraOperator',
    'CParachute',
    'CParachutedBallistics',
    'CParachutedContainer',
    'CParachutedJetBooster',
    'CParatroopersCreator',
    'CPhysPlatformRadioTurretAI',
    'CPlane',
    'CPlaneAI',
    'CPlaneInputController',
    'CPlatformInputController',
    'CPlatformTank',
    'CRobotCameraOperator',
    'CRocket',
    'CRopeNode',
    'CRopeSeg',
    'CSelector',
    'CSharedGroup',
    'CShip',
    'CShipAI',
    'CSolidDebris',
    'CSolidTrash',
    'CSpotlight',
    'CSpotter',
    'CStaticBlock',
    'CStaticEmitter',
    'CStaticExplosions',
    'CStaticVehicle',
    'CSubmarine',
    'CTank',
    'CTankCommandsPool',
    'CTankPlatformMonitor',
    'CTerrainArray',
    'CTorpedo',
    'CTowHook',
    'CTrackBody',
    'CTrackCamera',
    'CTrackHandler',
    'CTrackMission',
    'CTrainAI',
    'CTrainLocomotive',
    'CTrainWagon',
    'CTrash',
    'CTrashAnimated',
    'CTruck',
    'CTurret',
    'CTurretCamera',
    'CTurretRadioAI',
    'CTurretRadioAIInputController',
    'CTurretRiffle',
    'CUnmannedPlane',
    'CVehicleAI',
    'CVehicleExplosionTurret',
    'CVehicleInputController',
    'CVehicleMonitor',
    'CVehicleRangefinderTurret',
    'CVehicleRangefinderTurretAI',
    'CVehicleRocketTurret',
    'CVehicleRocketTurretAI',
    'CVehicleTorpedoTurret',
    'CVehicleTorpedoTurretAI',
    'CVehicleTurret',
    'CVehicleTurretAI',
    'CVehicleTurretInputController',
    'CVisorCamera',
    'CWindsock',
    'CWireRope',
)
