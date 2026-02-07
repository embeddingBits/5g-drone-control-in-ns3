#include "ns3/applications-module.h"
#include "ns3/command-line.h"
#include "ns3/config-store-module.h"
#include "ns3/internet-module.h"
#include "ns3/mmwave-helper.h"
#include "ns3/mmwave-point-to-point-epc-helper.h"
#include "ns3/mobility-module.h"
#include "ns3/point-to-point-helper.h"
#include "ns3/netanim-module.h"

using namespace ns3;
using namespace mmwave;

NS_LOG_COMPONENT_DEFINE("EpcFirstExample");

int main(int argc, char* argv[])
{
    uint16_t numEnb = 1;
    uint16_t numUe = 1;
    double simTime = 2.0;
    double interPacketInterval = 100;
    double minDistance = 10.0;  
    double maxDistance = 150.0; 
    bool harqEnabled = true;
    bool rlcAmEnabled = false;

    // Command line arguments
    CommandLine cmd;
    cmd.AddValue("numEnb", "Number of eNBs", numEnb);
    cmd.AddValue("numUe", "Number of UEs per eNB", numUe);
    cmd.AddValue("simTime", "Total duration of the simulation [s])", simTime);
    cmd.AddValue("interPacketInterval", "Inter-packet interval [us])", interPacketInterval);
    cmd.AddValue("harq", "Enable Hybrid ARQ", harqEnabled);
    cmd.AddValue("rlcAm", "Enable RLC-AM", rlcAmEnabled);
    cmd.Parse(argc, argv);

    Config::SetDefault("ns3::MmWaveHelper::RlcAmEnabled", BooleanValue(rlcAmEnabled));
    Config::SetDefault("ns3::MmWaveHelper::HarqEnabled", BooleanValue(harqEnabled));
    Config::SetDefault("ns3::MmWaveFlexTtiMacScheduler::HarqEnabled", BooleanValue(harqEnabled));
    Config::SetDefault("ns3::LteRlcAm::ReportBufferStatusTimer", TimeValue(MicroSeconds(100.0)));
    Config::SetDefault("ns3::LteRlcUmLowLat::ReportBufferStatusTimer",
                       TimeValue(MicroSeconds(100.0)));

    Ptr<MmWaveHelper> mmwaveHelper = CreateObject<MmWaveHelper>();
    mmwaveHelper->SetSchedulerType("ns3::MmWaveFlexTtiMacScheduler");
    Ptr<MmWavePointToPointEpcHelper> epcHelper = CreateObject<MmWavePointToPointEpcHelper>();
    mmwaveHelper->SetEpcHelper(epcHelper);
    mmwaveHelper->SetHarqEnabled(harqEnabled);

    ConfigStore inputConfig;
    inputConfig.ConfigureDefaults();

    cmd.Parse(argc, argv);

    Ptr<Node> pgw = epcHelper->GetPgwNode();

    // Create a single RemoteHost
    NodeContainer remoteHostContainer;
    remoteHostContainer.Create(1);
    Ptr<Node> remoteHost = remoteHostContainer.Get(0);
    InternetStackHelper internet;
    internet.Install(remoteHostContainer);

    // Create the Internet
    PointToPointHelper p2ph;
    p2ph.SetDeviceAttribute("DataRate", DataRateValue(DataRate("100Gb/s")));
    p2ph.SetDeviceAttribute("Mtu", UintegerValue(1500));
    p2ph.SetChannelAttribute("Delay", TimeValue(Seconds(0.010)));
    NetDeviceContainer internetDevices = p2ph.Install(pgw, remoteHost);
    Ipv4AddressHelper ipv4h;
    ipv4h.SetBase("1.0.0.0", "255.0.0.0");
    Ipv4InterfaceContainer internetIpIfaces = ipv4h.Assign(internetDevices);
    // interface 0 is localhost, 1 is the p2p device
    Ipv4Address remoteHostAddr = internetIpIfaces.GetAddress(1);

    Ipv4StaticRoutingHelper ipv4RoutingHelper;
    Ptr<Ipv4StaticRouting> remoteHostStaticRouting =
        ipv4RoutingHelper.GetStaticRouting(remoteHost->GetObject<Ipv4>());
    remoteHostStaticRouting->AddNetworkRouteTo(Ipv4Address("7.0.0.0"), Ipv4Mask("255.0.0.0"), 1);
  
  
    NodeContainer ueNodes;
    NodeContainer enbNodes;
    enbNodes.Create(numEnb);
    ueNodes.Create(numUe);
}
