# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The Python implementation of the GRPC helloworld.Greeter server."""

from concurrent import futures

import grpc
import time
import multiprocessing

import helloworld_pb2
import helloworld_pb2_grpc


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)


def request(port, message):
    channel = grpc.insecure_channel('localhost:' + str(port))
    stub = helloworld_pb2_grpc.GreeterStub(channel)
    response = stub.SayHello(helloworld_pb2.HelloRequest(name=message))
    print("Received: " + response.message)


def serve(port) -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    return server


def multiprocess(event: multiprocessing.Event):
    request(50051, 'hello')
    server = serve(60051)

    event.set()
    time.sleep(10)
    server.stop(None)


def run():
    server = serve(50051)

    event = multiprocessing.Event()
    process = multiprocessing.Process(target=multiprocess, args=(event,))
    process.start()
    event.wait()

    server.stop(None)
    request(60051, 'hi')


if __name__ == '__main__':
    run()
