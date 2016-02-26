/**
 * Created by pwwpcheng on 2016/2/17.
 */
/* This js file translates stored data into readable manner
 * Includes: meter_name
 *           alarm settings
 *           etc.
*/
var comparison_operator_CN = {
    'gt': '大于',
    'ge': '大于等于',
    'eq': '等于',
    'le': '小于等于',
    'lt': '小于',
    'ne': '不等于'
};

var notification_type_CN = {
    'email': '邮件通知',
    'message': '消息通知',
    'link': '访问链接'
};

var bool_CN = {
    'True': '是',
    'true': '是',
    'False': '否',
    'false': '否'
};

var level_CN = {
    'low': '低',
    'moderate': '中',
    'critical': '高'
};

var statistic_CN = {
    'avg' : '平均值',
    'max' : '最大值',
    'min' : '最小值',
    'sum' : '总和',
    'count' : '计数'
};

var meter_name_CN = {
    'cpu':'cpu时间',
    'cpu_util':'cpu使用率',
    'disk.allocation':'磁盘已分配空间',
    'disk.capacity':'磁盘总容量',
    'disk.read.bytes':'磁盘读取数据量',
    'disk.read.bytes.rate':'磁盘读取速率',
    'disk.read.requests':'磁盘读取请求数',
    'disk.read.requests.rate':'磁盘读取请求速率',
    'disk.root.size':'磁盘总空间*',
    'disk.usage':'磁盘使用率',
    'disk.write.bytes':'磁盘写入数据量',
    'disk.write.bytes.rate':'磁盘写入数据速率',
    'disk.write.requests':'磁盘写入请求数',
    'disk.write.requests.rate':'磁盘写入请求速率',
    'disk.device.allocation':'磁盘设备已分配空间',
    'disk.device.capacity':'磁盘设备总容量',
    'disk.device.read.bytes':'磁盘设备读取数据量',
    'disk.device.read.bytes.rate':'磁盘设备读取速率',
    'disk.device.read.requests':'磁盘设备读取请求数',
    'disk.device.read.requests.rate':'磁盘设备读取请求速率',
    'disk.device.root.size':'磁盘设备总空间*',
    'disk.device.usage':'磁盘设备使用率',
    'disk.device.write.bytes':'磁盘设备写入数据量',
    'disk.device.write.bytes.rate':'磁盘设备写入数据速率',
    'disk.device.write.requests':'磁盘设备写入请求数',
    'disk.device.write.requests.rate':'磁盘设备写入请求速率',
    'hardware.cpu.load.15min':'cpu15分钟内负载',
    'hardware.cpu.load.1min':'cpu1分钟内负载',
    'hardware.cpu.load.5min':'cpu5分钟内负载',
    'hardware.disk.size.total':'磁盘总空间',
    'hardware.disk.size.used':'磁盘已使用空间',
    'hardware.memory.swap.avail':'内存空闲交换空间',
    'hardware.memory.swap.total':'内存总的交换空间',
    'hardware.memory.total':'内存总大小',
    'hardware.memory.used':'内存已使用量',
    'hardware.network.incoming.bytes':'网卡流入字节数',
    'hardware.network.ip.incoming.datagrams':'网卡流入数据报数',
    'hardware.network.ip.outgoing.datagrams':'网卡输出数据报数',
    'hardware.network.outgoing.bytes':'网络输出字节数',
    'hardware.network.outgoing.errors':'网络输出坏数据报数',
    'image':'镜像名称存在',
    'image.size':'镜像大小',
    'instance':'实例存在',
    'instance:m1.small':'small实例类型',
    'memory':'内存总量',
    'memory.resident':'内存驻留空间',
    'memory.usage':'内存使用率',
    'network.incoming.bytes':'网卡流入字节数',
    'network.incoming.bytes.rate':'网卡流入字节数率',
    'network.incoming.packets':'网卡流入数据报数',
    'network.incoming.packets.rate':'网卡流入数据报数速率',
    'network.outgoing.bytes':'网卡输出字节数',
    'network.outgoing.bytes.rate':'网卡输出字节数速率',
    'network.outgoing.packets':'网卡输出数据报数',
    'network.outgoing.packets.rate':'网卡输出数据报数速率',
    'vcpus':'虚拟CPU数'
};

var machine_type_CN ={
    'vm' : '虚拟机',
    'pm' : '物理机'
};

var alarm_state_CN = {
    'alarm': '报警',
    'ok': '正常',
    'insufficient data': '数据不足'
};

var enabled_CN = bool_CN;
var repeat_actions_CN = bool_CN;

function translate_name(name, type){
    /*
     * Function "translate" translates "name" into translation of desired language
     *
     * Usage: translate(name, type, [language])
     * param name: name to be translated
     * param type: type of name (e.g. meter_name | comparison_operator| ...)
     * (hidden parameter) language: language for translation. Default: CN
     * return: translated string
     */
    var language = arguments[2] ? arguments[2] : 'CN';
    try {
        return eval(type + '_' + language + '["' + name + '"]');
    }catch(e){
        if (e instanceof EvalError) {
            console.info('Eval Error: In translating "'+ name+ '" of type "'+type+'"');
            return name;
        }
        else if (e instanceof ReferenceError) {
            console.info('Reference Error: In translating "' + name + '" of type "' + type + '"');
            return name;
        }
        else
            // Unknown error won't be handled
            throw e;
    }

}