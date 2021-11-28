
class Coalition:
    neutral = 0
    coal_1 = 1
    coal_2 = 2

    Allies = 1
    Axis = 2
    Entente = 3
    CentralPowers = 4


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


COUNTRIES_COALITION_DEFAULT = {
    Country.neutral: Coalition.neutral,

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
}


GAME_CLASSES = (
    'CAeroplaneFragment',
    'CAerostat',
    'CAerostatAI',
    'CAIPoi',
    'CAirfield',
    'CAnimationOperator',
    'CAttachedVehicle',
    'CBallistics',
    'CBanner',
    'CBatchBallistics',
    'CBatchExplosion',
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
    'CCloudSky',
    'CClusterBallistics',
    'CCommanderInputController',
    'CComplexTrigger',
    'CCumulativeRocket',
    'CDFMission',
    'CDistantLOD',
    'CDummyObject',
    'CEjectionPlace',
    'CEjectorController',
    'CFlag',
    'CFlareGun',
    'CFlexRope',
    'CForestBody',
    'CGameChat',
    'CGameMission',
    'CInfluenceArea',
    'CMouseControlCameraOperator',
    'CParachute',
    'CParachutedContainer',
    'CParatroopersCreator',
    'CPhysPlatformRadioTurretAI',
    'CPlane',
    'CPlaneAI',
    'CPlaneInputController',
    'CPlatformTank',
    'CRobotCameraOperator',
    'CRocket',
    'CRopeNode',
    'CRopeSeg',
    'CSharedGroup',
    'CShip',
    'CShipAI',
    'CSolidTrash',
    'CSpotlight',
    'CSpotter',
    'CStaticBlock',
    'CStaticEmitter',
    'CStaticVehicle',
    'CSubmarine',
    'CTank',
    'CTerrainArray',
    'CTorpedo',
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
    'CVehicleAI',
    'CVehicleExplosionTurret',
    'CVehicleInputController',
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
